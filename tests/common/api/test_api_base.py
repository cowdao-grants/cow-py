from unittest.mock import AsyncMock, Mock, patch

import httpx
import pytest

from cow_py.common.api.api_base import ApiBase, APIConfig
from cow_py.common.api.decorators import DEFAULT_BACKOFF_OPTIONS
from cow_py.common.config import SupportedChainId
from httpx import Request

ERROR_MESSAGE = "💣💥 Booom!"
OK_RESPONSE = {"status": 200, "ok": True, "content": {"some": "data"}}


@pytest.fixture
def sut():
    class MyConfig(APIConfig):
        def __init__(self):
            super().__init__(SupportedChainId.SEPOLIA, None)

        def get_base_url(self):
            return "http://localhost"

    class MyAPI(ApiBase):
        @staticmethod
        def get_config(context):
            return Mock(
                chain_id="mainnet", get_base_url=Mock(return_value="http://localhost")
            )

        async def get_version(self, context_override={}):
            return await self._fetch(
                path="/api/v1/version", context_override=context_override
            )

    return MyAPI(config=MyConfig())


@pytest.fixture
def mock_success_response():
    return AsyncMock(
        status_code=200,
        headers={"content-type": "application/json"},
        json=Mock(return_value=OK_RESPONSE),
    )


@pytest.fixture
def mock_http_status_error():
    return httpx.HTTPStatusError(
        message=ERROR_MESSAGE,
        request=Request("GET", "http://example.com"),
        response=httpx.Response(500),
    )


@pytest.mark.asyncio
async def test_no_re_attempt_if_success(sut, mock_success_response):
    with patch(
        "httpx.AsyncClient.send", side_effect=[mock_success_response]
    ) as mock_request:
        response = await sut.get_version()
        assert mock_request.awaited_once()
        assert response["content"]["some"] == "data"


@pytest.mark.asyncio
async def test_re_attempts_if_fails_then_succeeds(
    sut, mock_success_response, mock_http_status_error
):
    with patch(
        "httpx.AsyncClient.send",
        side_effect=[
            *([mock_http_status_error] * 3),
            mock_success_response,
        ],
    ) as mock_request:
        response = await sut.get_version()

        assert response["ok"] is True
        assert mock_request.call_count == 4


@pytest.mark.asyncio
async def test_succeeds_last_attempt(
    sut, mock_success_response, mock_http_status_error
):
    with patch(
        "httpx.AsyncClient.send",
        side_effect=[
            mock_http_status_error,
            mock_http_status_error,
            mock_success_response,
        ],
    ) as mock_send:
        response = await sut.get_version()
        assert response["ok"] is True
        assert mock_send.call_count == 3


@pytest.mark.asyncio
async def test_does_not_reattempt_after_max_failures(sut, mock_http_status_error):
    with patch(
        "httpx.AsyncClient.request", side_effect=[mock_http_status_error] * 3
    ) as mock_call:
        with pytest.raises(httpx.HTTPStatusError):
            await sut.get_version(context_override={"backoff_opts": {"max_tries": 3}})

        assert mock_call.call_count == 3


@pytest.mark.asyncio
async def test_backoff_uses_function_options_instead_of_default(
    sut, mock_http_status_error
):
    max_tries = 1

    assert max_tries != DEFAULT_BACKOFF_OPTIONS["max_tries"]

    with patch(
        "httpx.AsyncClient.request",
        side_effect=[mock_http_status_error] * max_tries,
    ) as mock_call:
        with pytest.raises(httpx.HTTPStatusError):
            await sut.get_version(
                context_override={"backoff_opts": {"max_tries": max_tries}}
            )

        assert mock_call.call_count == max_tries
