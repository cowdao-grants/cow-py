import pytest

from cowdao_cowpy.contracts.order import (
    Order,
    hashify,
    normalize_buy_token_balance,
    normalize_order,
    hash_order,
    hash_order_cancellation,
    hash_order_cancellations,
    OrderUidParams,
)
from .conftest import SAMPLE_DOMAIN, SAMPLE_ORDER


def test_order_dataclass():
    order = Order(
        sell_token="0x1111111111111111111111111111111111111111",
        buy_token="0x2222222222222222222222222222222222222222",
        receiver="0x3333333333333333333333333333333333333333",
        sell_amount=1000000000000000000,
        buy_amount=2000000000000000000,
        valid_to=1735689600,
        app_data="0x1234567890123456789012345678901234567890123456789012345678901234",
        fee_amount=1000000000000000,
        kind="sell",
    )

    assert order.sell_token == "0x1111111111111111111111111111111111111111"
    assert order.buyToken == "0x2222222222222222222222222222222222222222"
    assert order.sellAmount == 1000000000000000000


def test_hashify():
    assert (
        hashify(123)
        == "0x000000000000000000000000000000000000000000000000000000000000007b"
    )
    assert (
        hashify("1234")
        == "0x0000000000000000000000000000000000000000000000000000000000001234"
    )
    assert (
        hashify(b"\x12\x34")
        == "0x0000000000000000000000000000000000000000000000000000000000001234"
    )


def test_normalize_buy_token_balance():
    assert normalize_buy_token_balance(None) == "erc20"
    assert normalize_buy_token_balance("erc20") == "erc20"
    assert normalize_buy_token_balance("internal") == "internal"

    with pytest.raises(ValueError):
        normalize_buy_token_balance("invalid")


def test_normalize_order():
    normalized = normalize_order(SAMPLE_ORDER)

    assert normalized["sellToken"] == SAMPLE_ORDER.sell_token
    assert normalized["buyToken"] == SAMPLE_ORDER.buy_token
    assert normalized["sellAmount"] == SAMPLE_ORDER.sell_amount
    assert normalized["kind"] == SAMPLE_ORDER.kind
    assert normalized["partiallyFillable"] == SAMPLE_ORDER.partially_fillable
    assert normalized["sellTokenBalance"] == "erc20"
    assert normalized["buyTokenBalance"] == "erc20"


def test_hash_order():
    order_hash = hash_order(SAMPLE_DOMAIN, SAMPLE_ORDER)
    assert isinstance(order_hash, bytes)
    assert len(order_hash) == 32


def test_hash_order_cancellation():
    order_uid = b"0" * 56
    cancellation_hash = hash_order_cancellation(SAMPLE_DOMAIN, order_uid.hex())
    assert isinstance(cancellation_hash, str)
    assert len(cancellation_hash) == 64  # 32 bytes in hex


def test_hash_order_cancellations():
    order_uids = [b"0" * 56, b"1" * 56]
    cancellations_hash = hash_order_cancellations(
        SAMPLE_DOMAIN, [uid.hex() for uid in order_uids]
    )
    assert isinstance(cancellations_hash, str)
    assert len(cancellations_hash) == 64  # 32 bytes in hex


def test_order_uid_params():
    params = OrderUidParams(
        order_digest="0x1234567890123456789012345678901234567890123456789012345678901234",
        owner="0x1111111111111111111111111111111111111111",
        validTo=1735689600,
    )

    assert (
        params.order_digest
        == "0x1234567890123456789012345678901234567890123456789012345678901234"
    )
    assert params.owner == "0x1111111111111111111111111111111111111111"
    assert params.validTo == 1735689600
