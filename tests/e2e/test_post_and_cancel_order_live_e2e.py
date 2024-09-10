# To run this test you will need to fill the .env file with the necessary variables (see .env.example).
# You will also need to have enough funds in you wallet of the sell token to create the order.
# The funds have to already be approved to the CoW Swap Vault Relayer

import os
from dataclasses import asdict

import pytest
from eth_account import Account
from eth_typing import Address

from cow_py.codegen.abi_handler import dict_keys_to_camel_case
from cow_py.common.chains import Chain
from cow_py.common.config import SupportedChainId
from cow_py.common.constants import CowContractAddress
from cow_py.contracts.domain import domain
from cow_py.contracts.order import Order
from cow_py.contracts.sign import SigningScheme, sign_order, sign_order_cancellation
from cow_py.order_book.api import OrderBookApi
from cow_py.order_book.config import OrderBookAPIConfigFactory
from cow_py.order_book.generated.model import (
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
        **{
            "sellToken": WXDAI_GNOSIS_MAINNET_ADDRESS,
            "buyToken": COW_TOKEN_GNOSIS_MAINNET_ADDRESS,
            "receiver": E2E_GNOSIS_MAINNET_TESTING_EOA_ADDRESS,
            "from": E2E_GNOSIS_MAINNET_TESTING_EOA_ADDRESS,
            "onchainOrder": False,
        }
    )

    mock_order_quote_side = OrderQuoteSide1(
        sellAmountBeforeFee=TokenAmount("1000000000000000000"),
        kind=OrderQuoteSideKindSell.sell,
    )

    quote = await order_book_api.post_quote(
        mock_order_quote_request, mock_order_quote_side
    )

    order = Order(
        **{
            "sell_token": WXDAI_GNOSIS_MAINNET_ADDRESS,
            "buy_token": COW_TOKEN_GNOSIS_MAINNET_ADDRESS,
            "receiver": E2E_GNOSIS_MAINNET_TESTING_EOA_ADDRESS,
            "sell_amount": (10**15).__str__(),
            "buy_amount": (10**20).__str__(),
            "valid_to": quote.quote.validTo,
            "fee_amount": "0",
            "kind": "sell",
            "partially_fillable": False,
            "sell_token_balance": "erc20",
            "buy_token_balance": "erc20",
            "app_data": "0x0000000000000000000000000000000000000000000000000000000000000000",
        }
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
