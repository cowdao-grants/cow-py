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
