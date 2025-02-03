# To run this test you will need to fill the .env file with the necessary variables (see .env.example).
# You will also need to have enough funds in you wallet of the sell token to create the order.
# The funds have to already be approved to the CoW Swap Vault Relayer

import os
from dataclasses import asdict

import pytest
from eth_account import Account
from eth_typing import Address

from cowdao_cowpy.codegen.abi_handler import dict_keys_to_camel_case
from cowdao_cowpy.common.chains import Chain
from cowdao_cowpy.common.config import SupportedChainId
from cowdao_cowpy.common.constants import CowContractAddress
from cowdao_cowpy.contracts.domain import domain
from cowdao_cowpy.contracts.order import Order
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
)


E2E_GNOSIS_MAINNET_TESTING_EOA_PRIVATE_KEY = os.getenv(
    "E2E_GNOSIS_MAINNET_TESTING_EOA_PRIVATE_KEY", ""
)

COW_TOKEN_GNOSIS_MAINNET_ADDRESS = "0x177127622c4A00F3d409B75571e12cB3c8973d3c"
WXDAI_GNOSIS_MAINNET_ADDRESS = "0xe91D153E0b41518A2Ce8Dd3D7944Fa863463a97d"

E2E_GNOSIS_MAINNET_TESTING_EOA = Account.from_key(
    E2E_GNOSIS_MAINNET_TESTING_EOA_PRIVATE_KEY
)
E2E_GNOSIS_MAINNET_TESTING_EOA_ADDRESS: Address = E2E_GNOSIS_MAINNET_TESTING_EOA.address


@pytest.mark.asyncio
async def test_post_and_cancel_order_live_e2e():
    order_book_api = OrderBookApi(
        config=OrderBookAPIConfigFactory.get_config(
            "prod", SupportedChainId.GNOSIS_CHAIN
        )
    )

    mock_order_quote_request = OrderQuoteRequest(
        sellToken=WXDAI_GNOSIS_MAINNET_ADDRESS,
        buyToken=COW_TOKEN_GNOSIS_MAINNET_ADDRESS,
        receiver=E2E_GNOSIS_MAINNET_TESTING_EOA_ADDRESS,
        from_=E2E_GNOSIS_MAINNET_TESTING_EOA_ADDRESS,  # type: ignore # pyright doesn't recognize `populate_by_name=True`.
        onchainOrder=False,
    )

    mock_order_quote_side = OrderQuoteSide1(
        sellAmountBeforeFee=TokenAmount("1000000000000000000"),
        kind=OrderQuoteSideKindSell.sell,
    )

    quote = await order_book_api.post_quote(
        mock_order_quote_request, mock_order_quote_side
    )

    order = Order(
        sell_token=WXDAI_GNOSIS_MAINNET_ADDRESS,
        buy_token=COW_TOKEN_GNOSIS_MAINNET_ADDRESS,
        receiver=str(E2E_GNOSIS_MAINNET_TESTING_EOA_ADDRESS),
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

    signature = sign_order(
        order_domain, order, E2E_GNOSIS_MAINNET_TESTING_EOA, SigningScheme.EIP712
    )

    order_uid = await order_book_api.post_order(
        OrderCreation(
            **{
                **dict_keys_to_camel_case(asdict(order)),
                "signature": signature.data,
                "signingScheme": ModelSigningScheme.eip712,
            }
        )
    )

    order_cancellation_signature = sign_order_cancellation(
        order_domain,
        order_uid.root,
        E2E_GNOSIS_MAINNET_TESTING_EOA,
        SigningScheme.EIP712,
    )

    cancellation_result = await order_book_api.delete_order(
        OrderCancellations(
            orderUids=[order_uid],
            signature=EcdsaSignature(root=order_cancellation_signature.data),
            signingScheme=EcdsaSigningScheme.eip712,
        )
    )

    assert cancellation_result == "Cancelled"
