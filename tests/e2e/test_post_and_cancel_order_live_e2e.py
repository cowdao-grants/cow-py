import logging
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

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

E2E_SEPOLIA_TESTING_EOA_PRIVATE_KEY = os.getenv(
    "E2E_SEPOLIA_TESTING_EOA_PRIVATE_KEY", ""
)

COW_TOKEN_SEPOLIA_ADDRESS = "0x0625aFB445C3B6B7B929342a04A22599fd5dBB59"
WETH_SEPOLIA_ADDRESS = "0xfFf9976782d46CC05630D1f6eBAb18b2324d6B14"

E2E_SEPOLIA_TESTING_EOA = Account.from_key(E2E_SEPOLIA_TESTING_EOA_PRIVATE_KEY)
E2E_SEPOLIA_TESTING_EOA_ADDRESS: Address = E2E_SEPOLIA_TESTING_EOA.address


@pytest.mark.vcr
@pytest.mark.asyncio
async def test_post_and_cancel_order_live_e2e():
    order_book_api = OrderBookApi(
        config=OrderBookAPIConfigFactory.get_config("prod", SupportedChainId.SEPOLIA)
    )

    mock_order_quote_request = OrderQuoteRequest(
        **{
            "sellToken": COW_TOKEN_SEPOLIA_ADDRESS,
            "buyToken": WETH_SEPOLIA_ADDRESS,
            "receiver": E2E_SEPOLIA_TESTING_EOA_ADDRESS,
            "from": E2E_SEPOLIA_TESTING_EOA_ADDRESS,
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
            "sell_token": COW_TOKEN_SEPOLIA_ADDRESS,
            "buy_token": WETH_SEPOLIA_ADDRESS,
            "receiver": E2E_SEPOLIA_TESTING_EOA_ADDRESS,
            "sell_amount": (10**16).__str__(),
            "buy_amount": (10**16).__str__(),
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
        chain=Chain.SEPOLIA,
        verifying_contract=CowContractAddress.SETTLEMENT_CONTRACT.value,
    )

    signature = sign_order(
        order_domain, order, E2E_SEPOLIA_TESTING_EOA, SigningScheme.EIP712
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
        order_domain, order_uid.root, E2E_SEPOLIA_TESTING_EOA, SigningScheme.EIP712
    )

    cancellation_result = await order_book_api.delete_order(
        OrderCancellations(
            orderUids=[order_uid],
            signature=EcdsaSignature(root=order_cancellation_signature.data),
            signingScheme=EcdsaSigningScheme.eip712,
        )
    )

    assert cancellation_result == "Cancelled"
