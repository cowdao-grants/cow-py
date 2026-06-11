"""
Offline (hermetic) version of the post-and-cancel order flow.

Mirrors tests/e2e/test_post_and_cancel_order_live_e2e.py but mocks the
orderbook HTTP API with pytest-httpx and signs with a throwaway key, so it
runs without secrets, funds, or network access. The EIP-712 signing and
signature recovery are real (offline) crypto.
"""

import json
from dataclasses import asdict

import pytest
from eth_account import Account
from pytest_httpx import HTTPXMock

from cowdao_cowpy.codegen.abi_handler import dict_keys_to_camel_case
from cowdao_cowpy.common.chains import Chain
from cowdao_cowpy.common.config import SupportedChainId
from cowdao_cowpy.common.constants import CowContractAddress
from cowdao_cowpy.contracts.domain import domain
from cowdao_cowpy.contracts.order import (
    CANCELLATIONS_TYPE_FIELDS,
    ORDER_TYPE_FIELDS,
    Order,
    hash_typed_data,
    normalize_order,
)
from cowdao_cowpy.contracts.sign import (
    SigningScheme,
    sign_order,
    sign_order_cancellation,
)
from cowdao_cowpy.order_book.api import OrderBookApi
from cowdao_cowpy.order_book.config import OrderBookAPIConfigFactory
from cowdao_cowpy.order_book.generated.model import (
    EcdsaSignature,
    EcdsaSigningScheme,
    OrderCancellations,
    OrderCreation,
    OrderQuoteRequest,
    OrderQuoteSide1,
    OrderQuoteSideKindSell,
    SigningScheme as ModelSigningScheme,
    TokenAmount,
    UID,
)

COW_TOKEN_GNOSIS_MAINNET_ADDRESS = "0x177127622c4A00F3d409B75571e12cB3c8973d3c"
WXDAI_GNOSIS_MAINNET_ADDRESS = "0xe91D153E0b41518A2Ce8Dd3D7944Fa863463a97d"
GNOSIS_PROD_BASE_URL = "https://api.cow.fi/xdai"
# Order UIDs are 56 bytes: order digest (32) + owner (20) + validTo (4).
FAKE_ORDER_UID = "0x" + "ab" * 56


@pytest.fixture
def throwaway_eoa():
    """An ephemeral account: signing is offline, no funds or secrets needed."""
    return Account.create()


@pytest.mark.asyncio
async def test_post_and_cancel_order_offline(throwaway_eoa, httpx_mock: HTTPXMock):
    """
    Post an order and cancel it against a mocked orderbook API, asserting the
    request serialization and the (real) EIP-712 signatures along the way.
    """
    eoa_address = throwaway_eoa.address

    httpx_mock.add_response(
        method="POST",
        url=f"{GNOSIS_PROD_BASE_URL}/api/v1/quote",
        json={
            "quote": {
                "sellToken": WXDAI_GNOSIS_MAINNET_ADDRESS,
                "buyToken": COW_TOKEN_GNOSIS_MAINNET_ADDRESS,
                "receiver": eoa_address,
                "sellAmount": "999949387471650457",
                "buyAmount": "3163764525186117644164",
                "feeAmount": "50612528349543",
                "validTo": 1893456000,
                "appData": "0x0000000000000000000000000000000000000000000000000000000000000000",
                "partiallyFillable": False,
                "sellTokenBalance": "erc20",
                "buyTokenBalance": "erc20",
                "kind": "sell",
                "signingScheme": "eip712",
            },
            "from": eoa_address,
            "expiration": "2026-01-01T00:00:00Z",
            "id": 123456,
            "verified": True,
        },
    )
    httpx_mock.add_response(
        method="POST",
        url=f"{GNOSIS_PROD_BASE_URL}/api/v1/orders",
        json=FAKE_ORDER_UID,
    )
    httpx_mock.add_response(
        method="DELETE",
        url=f"{GNOSIS_PROD_BASE_URL}/api/v1/orders",
        json="Cancelled",
    )

    order_book_api = OrderBookApi(
        config=OrderBookAPIConfigFactory.get_config(
            "prod", SupportedChainId.GNOSIS_CHAIN
        )
    )

    quote = await order_book_api.post_quote(
        OrderQuoteRequest(
            sellToken=WXDAI_GNOSIS_MAINNET_ADDRESS,
            buyToken=COW_TOKEN_GNOSIS_MAINNET_ADDRESS,
            receiver=eoa_address,
            from_=eoa_address,  # type: ignore # pyright doesn't recognize `populate_by_name=True`.
            onchainOrder=False,
        ),
        OrderQuoteSide1(
            sellAmountBeforeFee=TokenAmount("1000000000000000000"),
            kind=OrderQuoteSideKindSell.sell,
        ),
    )

    order = Order(
        sell_token=WXDAI_GNOSIS_MAINNET_ADDRESS,
        buy_token=COW_TOKEN_GNOSIS_MAINNET_ADDRESS,
        receiver=eoa_address,
        sell_amount=str(10**15),
        buy_amount=str(10**20),
        valid_to=quote.quote.validTo,
        fee_amount="0",
        kind="sell",
        partially_fillable=False,
        sell_token_balance="erc20",
        buy_token_balance="erc20",
        app_data="0x0000000000000000000000000000000000000000000000000000000000000000",
    )

    order_domain = domain(
        chain=Chain.GNOSIS,
        verifying_contract=CowContractAddress.SETTLEMENT_CONTRACT.value,
    )

    signature = sign_order(order_domain, order, throwaway_eoa, SigningScheme.EIP712)

    # The EIP-712 order signature recovers to the signer (real crypto, offline).
    order_digest = hash_typed_data(
        order_domain, {"Order": ORDER_TYPE_FIELDS}, normalize_order(order)
    )
    assert Account._recover_hash(order_digest, signature=signature.data) == eoa_address

    order_uid = await order_book_api.post_order(
        OrderCreation(
            **{
                **dict_keys_to_camel_case(asdict(order)),
                "signature": signature.data,
                "signingScheme": ModelSigningScheme.eip712,
            }
        )
    )

    # The returned UID round-trips through the client untouched.
    assert order_uid == UID(FAKE_ORDER_UID)

    # The order was serialized with camelCase keys and stringified amounts.
    (post_order_request,) = httpx_mock.get_requests(
        method="POST", url=f"{GNOSIS_PROD_BASE_URL}/api/v1/orders"
    )
    posted_body = json.loads(post_order_request.content)
    assert {
        "sellToken",
        "buyToken",
        "sellAmount",
        "buyAmount",
        "validTo",
        "feeAmount",
        "partiallyFillable",
        "appData",
        "signingScheme",
    } <= posted_body.keys()
    assert posted_body["sellAmount"] == str(10**15)
    assert posted_body["buyAmount"] == str(10**20)
    assert isinstance(posted_body["sellAmount"], str)
    assert isinstance(posted_body["buyAmount"], str)
    assert posted_body["signature"] == signature.data

    order_cancellation_signature = sign_order_cancellation(
        order_domain, order_uid.root, throwaway_eoa, SigningScheme.EIP712
    )

    # The cancellation signature also recovers to the signer.
    cancellation_digest = hash_typed_data(
        order_domain,
        {"OrderCancellations": CANCELLATIONS_TYPE_FIELDS},
        {"orderUids": [order_uid.root]},
    )
    assert (
        Account._recover_hash(
            cancellation_digest, signature=order_cancellation_signature.data
        )
        == eoa_address
    )

    cancellation_result = await order_book_api.delete_order(
        OrderCancellations(
            orderUids=[order_uid],
            signature=EcdsaSignature(root=order_cancellation_signature.data),
            signingScheme=EcdsaSigningScheme.eip712,
        )
    )

    assert cancellation_result == "Cancelled"

    (delete_request,) = httpx_mock.get_requests(
        method="DELETE", url=f"{GNOSIS_PROD_BASE_URL}/api/v1/orders"
    )
    deleted_body = json.loads(delete_request.content)
    assert deleted_body["orderUids"] == [FAKE_ORDER_UID]
    assert deleted_body["signature"] == order_cancellation_signature.data
