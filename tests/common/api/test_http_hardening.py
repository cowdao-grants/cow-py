from typing import Optional

import httpx
import pytest
from pytest_httpx import HTTPXMock

from cowdao_cowpy.common.api.api_base import USER_AGENT, ApiBase, APIConfig
from cowdao_cowpy.common.api.errors import ApiResponseError
from cowdao_cowpy.common.config import SupportedChainId

OK_RESPONSE = {"ok": True}

BASE_URL = "http://localhost"
PARTNER_BASE_URL = "http://partner.localhost"

FAST_BACKOFF = {"backoff_opts": {"max_tries": 3, "jitter": None, "factor": 0.01}}


def make_sut(
    bearer_token: Optional[str] = None,
    api_key: Optional[str] = None,
    client: Optional[httpx.AsyncClient] = None,
):
    class MyConfig(APIConfig):
        config_map = {SupportedChainId.SEPOLIA: BASE_URL}
        partner_config_map = {SupportedChainId.SEPOLIA: PARTNER_BASE_URL}

        def __init__(self):
            super().__init__(
                SupportedChainId.SEPOLIA,
                None,
                bearer_token=bearer_token,
                api_key=api_key,
            )

    class MyAPI(ApiBase):
        async def get_version(self, context_override={}):
            return await self._fetch(
                path="/api/v1/version", context_override=context_override
            )

    return MyAPI(config=MyConfig(), client=client)


@pytest.mark.asyncio
async def test_sends_user_agent_and_default_headers(httpx_mock: HTTPXMock):
    httpx_mock.add_response(json=OK_RESPONSE)

    await make_sut().get_version()

    request = httpx_mock.get_requests()[0]
    assert request.headers["user-agent"] == USER_AGENT
    assert request.headers["accept"] == "application/json"
    assert request.headers["content-type"] == "application/json"


@pytest.mark.asyncio
async def test_no_auth_headers_by_default(httpx_mock: HTTPXMock):
    httpx_mock.add_response(json=OK_RESPONSE)

    await make_sut().get_version()

    request = httpx_mock.get_requests()[0]
    assert "authorization" not in request.headers
    assert "x-api-key" not in request.headers


@pytest.mark.asyncio
async def test_bearer_token_sets_authorization_header(httpx_mock: HTTPXMock):
    httpx_mock.add_response(json=OK_RESPONSE)

    await make_sut(bearer_token="my-token").get_version()

    request = httpx_mock.get_requests()[0]
    assert request.headers["authorization"] == "Bearer my-token"


@pytest.mark.asyncio
async def test_api_key_sets_header_and_partner_gateway_url(httpx_mock: HTTPXMock):
    httpx_mock.add_response(url=f"{PARTNER_BASE_URL}/api/v1/version", json=OK_RESPONSE)

    await make_sut(api_key="my-key").get_version()

    request = httpx_mock.get_requests()[0]
    assert request.headers["x-api-key"] == "my-key"
    assert str(request.url) == f"{PARTNER_BASE_URL}/api/v1/version"


@pytest.mark.asyncio
async def test_context_override_auth_headers(httpx_mock: HTTPXMock):
    httpx_mock.add_response(json=OK_RESPONSE)

    await make_sut().get_version(context_override={"bearer_token": "override-token"})

    request = httpx_mock.get_requests()[0]
    assert request.headers["authorization"] == "Bearer override-token"


@pytest.mark.asyncio
async def test_context_override_api_key_routes_to_partner_gateway(
    httpx_mock: HTTPXMock,
):
    httpx_mock.add_response(url=f"{PARTNER_BASE_URL}/api/v1/version", json=OK_RESPONSE)

    await make_sut().get_version(context_override={"api_key": "override-key"})

    request = httpx_mock.get_requests()[0]
    assert request.headers["x-api-key"] == "override-key"
    assert str(request.url) == f"{PARTNER_BASE_URL}/api/v1/version"


@pytest.mark.asyncio
async def test_partial_backoff_opts_merge_with_defaults(httpx_mock: HTTPXMock):
    # A partial override must keep the remaining defaults rather than
    # replacing them; with only max_tries given, retries must still happen
    # (and the merged opts must not lose keys like max_value).
    httpx_mock.add_response(status_code=429)
    httpx_mock.add_response(json=OK_RESPONSE)

    response = await make_sut().get_version(
        context_override={"backoff_opts": {"max_tries": 2, "factor": 0.01}}
    )

    assert response == OK_RESPONSE
    assert len(httpx_mock.get_requests()) == 2


@pytest.mark.asyncio
async def test_retries_429_then_succeeds(httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=429)
    httpx_mock.add_response(json=OK_RESPONSE)

    response = await make_sut().get_version(context_override=FAST_BACKOFF)

    assert response == OK_RESPONSE
    assert len(httpx_mock.get_requests()) == 2


@pytest.mark.asyncio
async def test_403_fails_immediately_without_retry(httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=403, text="blocked")

    with pytest.raises(ApiResponseError) as exc_info:
        await make_sut().get_version(context_override=FAST_BACKOFF)

    assert exc_info.value.error_type == "403"
    assert len(httpx_mock.get_requests()) == 1


@pytest.mark.asyncio
async def test_error_type_preserved_from_error_response_body(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        status_code=400,
        json={"errorType": "InsufficientBalance", "description": "not enough funds"},
    )

    with pytest.raises(ApiResponseError) as exc_info:
        await make_sut().get_version(context_override=FAST_BACKOFF)

    assert exc_info.value.error_type == "InsufficientBalance"
    assert len(httpx_mock.get_requests()) == 1


@pytest.mark.asyncio
async def test_error_type_in_ok_body_not_rewrapped(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        json={"errorType": "NoLiquidity", "description": "no liquidity"}
    )

    with pytest.raises(ApiResponseError) as exc_info:
        await make_sut().get_version()

    assert exc_info.value.error_type == "NoLiquidity"


@pytest.mark.asyncio
async def test_injected_client_is_reused_and_left_open(httpx_mock: HTTPXMock):
    httpx_mock.add_response(json=OK_RESPONSE)
    httpx_mock.add_response(json=OK_RESPONSE)

    client = httpx.AsyncClient()
    sut = make_sut(client=client)

    await sut.get_version()
    await sut.get_version()

    assert sut._get_client() is client
    assert not client.is_closed
    assert len(httpx_mock.get_requests()) == 2
    await client.aclose()


@pytest.mark.asyncio
async def test_lazy_client_created_once_and_reused(httpx_mock: HTTPXMock):
    httpx_mock.add_response(json=OK_RESPONSE)
    httpx_mock.add_response(json=OK_RESPONSE)

    sut = make_sut()

    await sut.get_version()
    first_client = sut._client
    await sut.get_version()

    assert first_client is not None
    assert sut._client is first_client
    assert not first_client.is_closed

    await sut.aclose()
    assert first_client.is_closed


@pytest.mark.asyncio
async def test_order_book_api_accepts_injected_client(httpx_mock: HTTPXMock):
    from cowdao_cowpy.common.config import SupportedChainId
    from cowdao_cowpy.order_book.api import OrderBookApi
    from cowdao_cowpy.order_book.config import OrderBookAPIConfigFactory

    httpx_mock.add_response(url="https://api.cow.fi/xdai/api/v1/version", json="1.0.0")

    client = httpx.AsyncClient()
    order_book = OrderBookApi(
        config=OrderBookAPIConfigFactory.get_config(
            "prod", SupportedChainId.GNOSIS_CHAIN
        ),
        client=client,
    )

    await order_book.get_version()

    assert order_book._get_client() is client
    assert not client.is_closed
    await client.aclose()


STAGING_BASE_URL = "http://staging.localhost"


def make_env_sut():
    """A SUT whose ``with_env("staging")`` routes to a distinct base URL, so a
    request that switches env can be told apart from one that fell back to prod."""

    class StagingConfig(APIConfig):
        config_map = {SupportedChainId.SEPOLIA: STAGING_BASE_URL}
        partner_config_map = {SupportedChainId.SEPOLIA: STAGING_BASE_URL}

        def __init__(self):
            super().__init__(SupportedChainId.SEPOLIA, None)

    class ProdConfig(APIConfig):
        config_map = {SupportedChainId.SEPOLIA: BASE_URL}
        partner_config_map = {SupportedChainId.SEPOLIA: PARTNER_BASE_URL}

        def __init__(self):
            super().__init__(SupportedChainId.SEPOLIA, None)

        def with_env(self, env):
            return StagingConfig() if env == "staging" else self

    class MyAPI(ApiBase):
        async def get_version(self, context_override={}):
            return await self._fetch(
                path="/api/v1/version", context_override=context_override
            )

    return MyAPI(config=ProdConfig())


@pytest.mark.asyncio
async def test_env_override_survives_retry(httpx_mock: HTTPXMock):
    # Regression: backoff retries re-invoke _fetch with the *same*
    # context_override dict. The env override used to be popped on the first
    # attempt, so retries silently fell back to the default (prod) URL. Both
    # the initial 503 and its retry must target the staging URL.
    httpx_mock.add_response(
        url=f"{STAGING_BASE_URL}/api/v1/version", status_code=503, text="busy"
    )
    httpx_mock.add_response(url=f"{STAGING_BASE_URL}/api/v1/version", json=OK_RESPONSE)

    response = await make_env_sut().get_version(
        context_override={"env": "staging", **FAST_BACKOFF}
    )

    assert response == OK_RESPONSE
    requests = httpx_mock.get_requests()
    assert len(requests) == 2
    assert all(
        str(request.url) == f"{STAGING_BASE_URL}/api/v1/version" for request in requests
    )
