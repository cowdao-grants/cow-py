# test_serialization_warnings.py
import json
import warnings

from cowdao_cowpy.order_book.generated.model import (
    BuyTokenDestination,
    OrderCreation,
    OrderQuoteRequest,
    PriceQuality,
    SellTokenSource,
    SigningScheme,
)


def _dump_without_user_warnings(model):
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        dumped = model.model_dump_json(by_alias=True)
    user_warnings = [w for w in caught if issubclass(w.category, UserWarning)]
    assert (
        user_warnings == []
    ), f"unexpected UserWarnings: {[str(w.message) for w in user_warnings]}"
    return json.loads(dumped)


def test_order_quote_request_defaults_serialize_without_warnings():
    order_quote_request = OrderQuoteRequest(
        sellToken="0x6810e776880c02933d47db1b9fc05908e5386b96",
        buyToken="0xdef1ca1fb7fbcdc777520aa7f396b4e015f497ab",
        from_="0xfb3c7eb936caa12b5a884d612393969a557d4307",  # type: ignore # pyright doesn't recognize `populate_by_name=True`.
        appData="0x0000000000000000000000000000000000000000000000000000000000000000",
    )

    data = _dump_without_user_warnings(order_quote_request)

    assert data["sellTokenBalance"] == "erc20"
    assert data["buyTokenBalance"] == "erc20"
    assert data["priceQuality"] == "verified"
    assert data["signingScheme"] == "eip712"

    assert order_quote_request.sellTokenBalance is SellTokenSource.erc20
    assert order_quote_request.buyTokenBalance is BuyTokenDestination.erc20
    assert order_quote_request.priceQuality is PriceQuality.verified
    assert order_quote_request.signingScheme is SigningScheme.eip712


def test_order_creation_defaults_serialize_without_warnings():
    # The omitted defaulted fields are exactly what this test exercises.
    order_creation = OrderCreation(  # type: ignore[reportCallIssue]
        sellToken="0x6810e776880c02933d47db1b9fc05908e5386b96",
        buyToken="0xdef1ca1fb7fbcdc777520aa7f396b4e015f497ab",
        sellAmount="1",
        buyAmount="1",
        validTo=0,
        feeAmount="0",
        kind="sell",
        partiallyFillable=False,
        appData="0x0000000000000000000000000000000000000000000000000000000000000000",
        signingScheme="eip712",
        signature="0x",
    )

    data = _dump_without_user_warnings(order_creation)

    assert data["sellTokenBalance"] == "erc20"
    assert data["buyTokenBalance"] == "erc20"
    assert data["signingScheme"] == "eip712"

    assert order_creation.sellTokenBalance is SellTokenSource.erc20
    assert order_creation.buyTokenBalance is BuyTokenDestination.erc20
    assert order_creation.signingScheme is SigningScheme.eip712
