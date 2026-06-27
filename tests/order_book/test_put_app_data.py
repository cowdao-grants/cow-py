import pytest
from pytest_httpx import HTTPXMock

from cowdao_cowpy.common.config import SupportedChainId
from cowdao_cowpy.order_book.api import OrderBookApi
from cowdao_cowpy.order_book.config import OrderBookAPIConfigFactory
from cowdao_cowpy.order_book.generated.model import (
    AppData,
    AppDataHash,
    AppDataObject,
)

APP_DATA_HASH = "0x971c41b97f59534448ab833b0d83f755a4bc5c29f92b01776faa3699fcb0eeae"


@pytest.mark.asyncio
async def test_put_app_data_uses_bare_hash_in_url(httpx_mock: HTTPXMock):
    # Regression test: interpolating the AppDataHash model produced
    # "/app_data/root='0x...'" URLs, which the API rejects with HTTP 400.
    httpx_mock.add_response(
        method="PUT",
        url=f"https://api.cow.fi/xdai/api/v1/app_data/{APP_DATA_HASH}",
        json=APP_DATA_HASH,
    )

    order_book = OrderBookApi(
        config=OrderBookAPIConfigFactory.get_config(
            "prod", SupportedChainId.GNOSIS_CHAIN
        )
    )
    result = await order_book.put_app_data(
        AppDataObject(fullAppData=AppData('{"appCode":"test"}')),
        AppDataHash(root=APP_DATA_HASH),
    )

    (request,) = httpx_mock.get_requests()
    assert request.url.path == f"/xdai/api/v1/app_data/{APP_DATA_HASH}"
    assert "root=" not in str(request.url)
    assert result == AppDataHash(root=APP_DATA_HASH)
