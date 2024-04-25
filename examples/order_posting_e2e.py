# To run this test you will need to fill the .env file with the necessary variables (see .env.example).
# You will also need to have enough funds in you wallet of the sell token to create the order.
# The funds have to already be approved to the CoW Swap Vault Relayer

import asyncio
import json
import os
from dataclasses import asdict

from web3 import Account

from cow_py.common.chains import Chain
from cow_py.common.config import SupportedChainId
from cow_py.common.constants import CowContractAddress
from cow_py.contracts.domain import domain
from cow_py.contracts.order import Order
from cow_py.contracts.sign import EcdsaSignature, SigningScheme
from cow_py.contracts.sign import sign_order as _sign_order
from cow_py.order_book.api import OrderBookApi
from cow_py.order_book.config import OrderBookAPIConfigFactory
from cow_py.order_book.generated.model import OrderQuoteSide1, TokenAmount
from cow_py.order_book.generated.model import OrderQuoteSideKindSell
from cow_py.order_book.generated.model import (
    UID,
    OrderCreation,
    OrderQuoteRequest,
    OrderQuoteResponse,
)

BUY_TOKEN = "0xfFf9976782d46CC05630D1f6eBAb18b2324d6B14"  # WETH
SELL_TOKEN = "0xbe72E441BF55620febc26715db68d3494213D8Cb"  # USDC
SELL_AMOUNT_BEFORE_FEE = "10000000000000000000"  # 100 USDC with 18 decimals
ORDER_KIND = "sell"
CHAIN = Chain.SEPOLIA
CHAIN_ID = SupportedChainId.SEPOLIA

config = OrderBookAPIConfigFactory.get_config("prod", CHAIN_ID)
ORDER_BOOK_API = OrderBookApi(config)

ADDRESS = os.getenv("USER_ADDRESS")
ACCOUNT = Account.from_key(os.getenv("PRIVATE_KEY"))


async def get_order_quote(
    order_quote_request: OrderQuoteRequest, order_side: OrderQuoteSide1
) -> OrderQuoteResponse:
    return await ORDER_BOOK_API.post_quote(order_quote_request, order_side)


def sign_order(order: Order) -> EcdsaSignature:
    order_domain = asdict(
        domain(
            chain=CHAIN, verifying_contract=CowContractAddress.SETTLEMENT_CONTRACT.value
        )
    )
    del order_domain["salt"]  # TODO: improve interfaces

    return _sign_order(order_domain, order, ACCOUNT, SigningScheme.EIP712)


async def post_order(order: Order, signature: EcdsaSignature) -> UID:
    order_creation = OrderCreation(
        **{
            "from": ADDRESS,
            "sellToken": order.sellToken,
            "buyToken": order.buyToken,
            "sellAmount": order.sellAmount,
            "feeAmount": order.feeAmount,
            "buyAmount": order.buyAmount,
            "validTo": order.validTo,
            "kind": order.kind,
            "partiallyFillable": order.partiallyFillable,
            "appData": order.appData,
            "signature": signature.data,
            "signingScheme": "eip712",
            "receiver": order.receiver,
        },
    )
    return await ORDER_BOOK_API.post_order(order_creation)


async def main():
    order_quote_request = OrderQuoteRequest(
        **{
            "sellToken": SELL_TOKEN,
            "buyToken": BUY_TOKEN,
            "from": ADDRESS,
        }
    )
    order_side = OrderQuoteSide1(
        kind=OrderQuoteSideKindSell.sell,
        sellAmountBeforeFee=TokenAmount(SELL_AMOUNT_BEFORE_FEE),
    )

    order_quote = await get_order_quote(order_quote_request, order_side)

    order_quote_dict = json.loads(order_quote.quote.model_dump_json(by_alias=True))
    order = Order(
        **{
            "sellToken": SELL_TOKEN,
            "buyToken": BUY_TOKEN,
            "receiver": ADDRESS,
            "validTo": order_quote_dict["validTo"],
            "appData": "0x0000000000000000000000000000000000000000000000000000000000000000",
            "sellAmount": SELL_AMOUNT_BEFORE_FEE,  # Since it is a sell order, the sellAmountBeforeFee is the same as the sellAmount
            "buyAmount": order_quote_dict["buyAmount"],
            "feeAmount": "0",  # CoW Swap does not charge fees
            "kind": ORDER_KIND,
            "sellTokenBalance": "erc20",
            "buyTokenBalance": "erc20",
        }
    )

    signature = sign_order(order)
    order_uid = await post_order(order, signature)
    print(f"order posted on link: {ORDER_BOOK_API.get_order_link(order_uid)}")


if __name__ == "__main__":
    asyncio.run(main())
