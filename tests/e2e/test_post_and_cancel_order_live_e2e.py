import logging
import os
from dataclasses import asdict

import pytest
from eth_account import Account
from eth_typing import Address

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
    logger.info("Starting E2E test: Post and Cancel Order")

    order_book_api = OrderBookApi(
        config=OrderBookAPIConfigFactory.get_config("prod", SupportedChainId.SEPOLIA)
    )
    logger.info("Initialized OrderBookApi with Sepolia configuration")

    mock_order_quote_request = OrderQuoteRequest(
        **{
            "sellToken": COW_TOKEN_SEPOLIA_ADDRESS,
            "buyToken": WETH_SEPOLIA_ADDRESS,
            "receiver": E2E_SEPOLIA_TESTING_EOA_ADDRESS,
            "from": E2E_SEPOLIA_TESTING_EOA_ADDRESS,
            "onchainOrder": False,
        }
    )
    logger.info(f"Created mock order quote request: {mock_order_quote_request}")

    mock_order_quote_side = OrderQuoteSide1(
        sellAmountBeforeFee=TokenAmount("1000000000000000000"),
        kind=OrderQuoteSideKindSell.sell,
    )
    logger.info(f"Created mock order quote side: {mock_order_quote_side}")

    quote = await order_book_api.post_quote(
        mock_order_quote_request, mock_order_quote_side
    )
    logger.info(f"Received quote: {quote}")

    order = Order(
        **{
            "sellToken": COW_TOKEN_SEPOLIA_ADDRESS,
            "buyToken": WETH_SEPOLIA_ADDRESS,
            "receiver": E2E_SEPOLIA_TESTING_EOA_ADDRESS,
            "sellAmount": (10**16).__str__(),
            "buyAmount": (10**16).__str__(),
            "validTo": quote.quote.validTo,
            "feeAmount": "0",
            "kind": "sell",
            "partiallyFillable": False,
            "sellTokenBalance": "erc20",
            "buyTokenBalance": "erc20",
            "appData": "0x0000000000000000000000000000000000000000000000000000000000000000",
        }
    )
    logger.info(f"Created order: {order}")

    order_domain = asdict(
        domain(
            chain=Chain.SEPOLIA,
            verifying_contract=CowContractAddress.SETTLEMENT_CONTRACT.value,
        )
    )
    del order_domain["salt"]
    logger.info(f"Created order domain: {order_domain}")

    signature = sign_order(
        order_domain, order, E2E_SEPOLIA_TESTING_EOA, SigningScheme.EIP712
    )
    logger.info(f"Signed order with signature: {signature}")

    order_uid = await order_book_api.post_order(
        OrderCreation(
            **{
                **asdict(order),
                "signature": signature.data,
                "signingScheme": ModelSigningScheme.eip712,
            }
        )
    )
    logger.info(f"Posted order, received UID: {order_uid}")

    order_cancellation_signature = sign_order_cancellation(
        order_domain, order_uid.root, E2E_SEPOLIA_TESTING_EOA, ModelSigningScheme.eip712
    )
    logger.info(f"Created order cancellation signature: {order_cancellation_signature}")

    cancellation_result = await order_book_api.delete_order(
        OrderCancellations(
            orderUids=[order_uid],
            signature=EcdsaSignature(root=order_cancellation_signature.data),
            signingScheme=EcdsaSigningScheme.eip712,
        )
    )
    logger.info(f"Cancelled order, result: {cancellation_result}")

    logger.info("E2E test completed successfully")
