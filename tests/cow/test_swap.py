"""
Offline tests for `swap_tokens`, focused on app-data registration.

Regression for the gap where a custom app-data hash was never uploaded: the
order referenced a hash the orderbook had never seen and was rejected. The fix
always registers the app-data document the order references.
"""

import json

import pytest
from eth_account import Account
from pytest_httpx import HTTPXMock
from web3 import Web3
from web3.types import Wei

from cowdao_cowpy.app_data.utils import (
    DEFAULT_APP_DATA_HASH,
    PartnerFee,
    _app_data_upload_cache,
    generate_app_data,
)
from cowdao_cowpy.common.chains import Chain
from cowdao_cowpy.cow.swap import swap_tokens
from cowdao_cowpy.order_book.generated.model import UID

GNOSIS_PROD_BASE_URL = "https://api.cow.fi/xdai"
WXDAI = Web3.to_checksum_address("0xe91D153E0b41518A2Ce8Dd3D7944Fa863463a97d")
COW = Web3.to_checksum_address("0x177127622c4A00F3d409B75571e12cB3c8973d3c")
SELL_AMOUNT = Wei(10**18)
FAKE_ORDER_UID = "0x" + "ab" * 56


@pytest.fixture(autouse=True)
def _clear_app_data_cache():
    # The upload cache is module-global; clear it so each test actually
    # exercises the PUT rather than hitting a warm cache from a sibling test.
    _app_data_upload_cache.clear()
    yield
    _app_data_upload_cache.clear()


@pytest.fixture
def throwaway_eoa():
    return Account.create()


def _add_quote_and_order_mocks(httpx_mock: HTTPXMock, receiver: str):
    httpx_mock.add_response(
        method="POST",
        url=f"{GNOSIS_PROD_BASE_URL}/api/v1/quote",
        json={
            "quote": {
                "sellToken": WXDAI,
                "buyToken": COW,
                "receiver": receiver,
                "sellAmount": "999949387471650457",
                "buyAmount": "3163764525186117644164",
                "feeAmount": "0",
                "validTo": 1893456000,
                "appData": "0x0000000000000000000000000000000000000000000000000000000000000000",
                "partiallyFillable": False,
                "sellTokenBalance": "erc20",
                "buyTokenBalance": "erc20",
                "kind": "sell",
                "signingScheme": "eip712",
                "gasAmount": "150000",
                "gasPrice": "15000000000",
                "sellTokenPrice": "1000000000",
            },
            "from": receiver,
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


def _put_app_data_request(httpx_mock: HTTPXMock):
    puts = [r for r in httpx_mock.get_requests() if r.method == "PUT"]
    assert len(puts) == 1, f"expected exactly one app_data upload, got {len(puts)}"
    return puts[0]


def _posted_order_app_data(httpx_mock: HTTPXMock) -> str:
    (order_request,) = httpx_mock.get_requests(
        method="POST", url=f"{GNOSIS_PROD_BASE_URL}/api/v1/orders"
    )
    return json.loads(order_request.content)["appData"]


@pytest.mark.asyncio
async def test_swap_uploads_custom_app_data_and_references_its_hash(
    throwaway_eoa, httpx_mock: HTTPXMock
):
    custom_app_code = "my-custom-dapp"
    expected_hash = generate_app_data(app_code=custom_app_code).app_data_hash.root
    assert expected_hash != DEFAULT_APP_DATA_HASH  # genuinely custom

    httpx_mock.add_response(
        method="PUT",
        url=f"{GNOSIS_PROD_BASE_URL}/api/v1/app_data/{expected_hash}",
        json=expected_hash,
    )
    _add_quote_and_order_mocks(httpx_mock, throwaway_eoa.address)

    completed = await swap_tokens(
        amount=SELL_AMOUNT,
        account=throwaway_eoa,
        chain=Chain.GNOSIS,
        sell_token=WXDAI,
        buy_token=COW,
        app_code=custom_app_code,
    )

    assert completed.uid == UID(FAKE_ORDER_UID)

    # The custom document was uploaded to its own hash...
    put_request = _put_app_data_request(httpx_mock)
    assert put_request.url.path.endswith(f"/api/v1/app_data/{expected_hash}")
    assert custom_app_code in json.loads(put_request.content)["fullAppData"]
    # ...and the posted order references that exact hash.
    assert _posted_order_app_data(httpx_mock) == expected_hash


@pytest.mark.asyncio
async def test_swap_uploads_default_app_data_when_no_overrides(
    throwaway_eoa, httpx_mock: HTTPXMock
):
    httpx_mock.add_response(
        method="PUT",
        url=f"{GNOSIS_PROD_BASE_URL}/api/v1/app_data/{DEFAULT_APP_DATA_HASH}",
        json=DEFAULT_APP_DATA_HASH,
    )
    _add_quote_and_order_mocks(httpx_mock, throwaway_eoa.address)

    completed = await swap_tokens(
        amount=SELL_AMOUNT,
        account=throwaway_eoa,
        chain=Chain.GNOSIS,
        sell_token=WXDAI,
        buy_token=COW,
    )

    assert completed.uid == UID(FAKE_ORDER_UID)
    put_request = _put_app_data_request(httpx_mock)
    assert put_request.url.path.endswith(f"/api/v1/app_data/{DEFAULT_APP_DATA_HASH}")
    assert _posted_order_app_data(httpx_mock) == DEFAULT_APP_DATA_HASH


@pytest.mark.asyncio
async def test_swap_partner_fee_appears_in_uploaded_doc(
    throwaway_eoa, httpx_mock: HTTPXMock
):
    partner_fee = PartnerFee(bps=100, recipient="0x" + "11" * 20)
    expected_hash = generate_app_data(partner_fee=partner_fee).app_data_hash.root

    httpx_mock.add_response(
        method="PUT",
        url=f"{GNOSIS_PROD_BASE_URL}/api/v1/app_data/{expected_hash}",
        json=expected_hash,
    )
    _add_quote_and_order_mocks(httpx_mock, throwaway_eoa.address)

    await swap_tokens(
        amount=SELL_AMOUNT,
        account=throwaway_eoa,
        chain=Chain.GNOSIS,
        sell_token=WXDAI,
        buy_token=COW,
        partner_fee=partner_fee,
    )

    put_request = _put_app_data_request(httpx_mock)
    full_app_data = json.loads(json.loads(put_request.content)["fullAppData"])
    assert full_app_data["metadata"]["partnerFee"] == {
        "bps": 100,
        "recipient": "0x" + "11" * 20,
    }
    assert _posted_order_app_data(httpx_mock) == expected_hash
