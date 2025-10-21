"""
Cancel all orders example.
"""

import os

from eth_account import Account
from cowdao_cowpy.common.chains import Chain
from cowdao_cowpy.common.config import SupportedChainId
from cowdao_cowpy.common.constants import CowContractAddress
from cowdao_cowpy.contracts.domain import domain
from cowdao_cowpy.contracts.sign import SigningScheme, sign_order_cancellation
from cowdao_cowpy.order_book.api import OrderBookApi
from cowdao_cowpy.order_book.config import OrderBookAPIConfigFactory
import asyncio

from cowdao_cowpy.order_book.generated.model import (
    EcdsaSignature,
    EcdsaSigningScheme,
    OrderCancellations,
    OrderStatus,
    UID,
)

PRIVATE_KEY = os.getenv("TEST_PRIVATE_KEY")

if not PRIVATE_KEY:
    raise ValueError("Missing variables on .env file")

ACCOUNT = Account.from_key(PRIVATE_KEY)


async def main():
    order_book_api = OrderBookApi(
        config=OrderBookAPIConfigFactory.get_config("prod", SupportedChainId.SEPOLIA)
    )

    orders = await order_book_api.get_orders_by_owner(ACCOUNT.address)
    open_orders = [order for order in orders if order.status == OrderStatus.open]
    print(f"Found {len(open_orders)} open orders to cancel.")

    order_domain = domain(
        chain=Chain.SEPOLIA,
        verifying_contract=CowContractAddress.SETTLEMENT_CONTRACT.value,
    )

    for order in open_orders:
        order_cancellation_signature = sign_order_cancellation(
            order_domain,
            order.uid.root,
            ACCOUNT,
            SigningScheme.EIP712,
        )

        cancellation_result = await order_book_api.delete_order(
            OrderCancellations(
                orderUids=[UID(order.uid.root)],
                signature=EcdsaSignature(root=order_cancellation_signature.data),
                signingScheme=EcdsaSigningScheme.eip712,
            )
        )
        print(
            f"Cancelled order with UID: {order.uid.root}, result: {cancellation_result}"
        )


if __name__ == "__main__":
    asyncio.run(main())
