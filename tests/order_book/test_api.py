from unittest.mock import AsyncMock, Mock, patch

import pytest

from cow_py.order_book.api import OrderBookApi
from cow_py.order_book.generated.model import OrderQuoteSide1
from cow_py.order_book.generated.model import OrderQuoteSideKindSell
from cow_py.order_book.generated.model import TokenAmount
from cow_py.order_book.generated.model import (
    OrderQuoteRequest,
    OrderQuoteResponse,
    Trade,
    OrderCreation,
)


@pytest.fixture
def order_book_api():
    return OrderBookApi()


@pytest.mark.asyncio
async def test_get_version(order_book_api):
    expected_version = "1.0.0"
    with patch("httpx.AsyncClient.request", new_callable=AsyncMock) as mock_request:
        mock_request.return_value = AsyncMock(
            status_code=200,
            text=expected_version,
        )
        version = await order_book_api.get_version()

        mock_request.assert_awaited_once()
        assert version == expected_version


@pytest.mark.asyncio
async def test_get_trades_by_order_uid(order_book_api):
    mock_trade_data = [
        {
            "blockNumber": 123456,
            "logIndex": 789,
            "orderUid": "mock_order_uid",
            "owner": "mock_owner_address",
            "sellToken": "mock_sell_token_address",
            "buyToken": "mock_buy_token_address",
            "sellAmount": "100",
            "sellAmountBeforeFees": "120",
            "buyAmount": "200",
            "txHash": "mock_transaction_hash",
        }
    ]
    mock_trade = Trade(**mock_trade_data[0])
    with patch("httpx.AsyncClient.request", new_callable=AsyncMock) as mock_request:
        mock_request.return_value = AsyncMock(
            status_code=200,
            headers={"content-type": "application/json"},
            json=Mock(return_value=mock_trade_data),
        )
        trades = await order_book_api.get_trades_by_order_uid("mock_order_uid")
        mock_request.assert_awaited_once()
        assert trades == [mock_trade]


@pytest.mark.asyncio
async def test_post_quote(order_book_api):
    mock_order_quote_request = OrderQuoteRequest(
        **{
            "sellToken": "0x",
            "buyToken": "0x",
            "receiver": "0x",
            "appData": "app_data_object",
            "appDataHash": "0x",
            "from": "0x",
            "priceQuality": "verified",
            "signingScheme": "eip712",
            "onchainOrder": False,
        }
    )

    mock_order_quote_side = OrderQuoteSide1(
        sellAmountBeforeFee=TokenAmount("0"), kind=OrderQuoteSideKindSell.sell
    )
    mock_order_quote_response_data = {
        "quote": {
            "sellToken": "0x",
            "buyToken": "0x",
            "receiver": "0x",
            "sellAmount": "0",
            "buyAmount": "0",
            "feeAmount": "0",
            "validTo": 0,
            "appData": "0x",
            "partiallyFillable": True,
            "sellTokenBalance": "erc20",
            "buyTokenBalance": "erc20",
            "kind": "buy",
        },
        "verified": True,
        "from": "0x",
        "expiration": "0",
    }
    mock_order_quote_response = OrderQuoteResponse(**mock_order_quote_response_data)
    with patch("httpx.AsyncClient.request", new_callable=AsyncMock) as mock_request:
        mock_request.return_value = AsyncMock(
            status_code=200,
            headers={"content-type": "application/json"},
            json=Mock(return_value=mock_order_quote_response_data),
        )
        response = await order_book_api.post_quote(
            mock_order_quote_request, mock_order_quote_side
        )
        mock_request.assert_awaited_once()
        assert response == mock_order_quote_response


@pytest.mark.asyncio
async def test_post_order(order_book_api):
    mock_response = "mock_uid"
    mock_order_creation = OrderCreation(
        **{
            "sellToken": "0x",
            "buyToken": "0x",
            "sellAmount": "0",
            "buyAmount": "0",
            "validTo": 0,
            "feeAmount": "0",
            "kind": "buy",
            "partiallyFillable": True,
            "appData": "0x",
            "signingScheme": "eip712",
            "signature": "0x",
            "receiver": "0x",
            "sellTokenBalance": "erc20",
            "buyTokenBalance": "erc20",
            "quoteId": 0,
            "appDataHash": "0x",
            "from_": "0x",
        }
    )
    with patch("httpx.AsyncClient.request", new_callable=AsyncMock) as mock_request:
        mock_request.return_value = AsyncMock(
            status_code=200,
            text=mock_response,
        )
        response = await order_book_api.post_order(mock_order_creation)
        mock_request.assert_awaited_once()
        assert response.root == mock_response
