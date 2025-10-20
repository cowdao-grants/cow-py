"""
Test the functionality of the token swapper module.
"""
# To run this test you will need to fill the .env file with the necessary variables (see .env.example).
# You will also need to have enough funds in you wallet of the sell token to create the order.
# The funds have to already be approved to the CoW Swap Vault Relayer

from datetime import datetime, timedelta
import os

import asyncio
from dotenv import load_dotenv
from web3 import Account
from web3.types import Wei
from cowdao_cowpy.common.chains import Chain
from cowdao_cowpy.cow.swap import (
    create_limit_buy_order,
    TokenSwapper,
    create_limit_sell_order,
)
from cowdao_cowpy.order_book.generated.model import Address

QUOTE_TOKEN = Address("0xbe72E441BF55620febc26715db68d3494213D8Cb")  # USDC
QUOTE_TOKEN_DECIMALS = 18
BASE_TOKEN = Address("0xfFf9976782d46CC05630D1f6eBAb18b2324d6B14")  # WETH
BASE_TOKEN_DECIMALS = 18
AMOUNT_BEFORE_FEE = Wei(int(0.1 * 10**BASE_TOKEN_DECIMALS))  # 0.1 WETH with 18 decimals
CHAIN = Chain.SEPOLIA

PRICE = 125.00  # Price in USDC

load_dotenv()

PRIVATE_KEY = os.getenv("TEST_PRIVATE_KEY")

if not PRIVATE_KEY:
    raise ValueError("Missing variables on .env file")

ACCOUNT = Account.from_key(PRIVATE_KEY)


async def do_buy(token_swapper: TokenSwapper):
    return await create_limit_buy_order(
        buy_amount=AMOUNT_BEFORE_FEE,
        price=PRICE,
        swapper=token_swapper,
        base_token=BASE_TOKEN,
        base_token_decimals=BASE_TOKEN_DECIMALS,
        quote_token_decimals=QUOTE_TOKEN_DECIMALS,
        quote_token=QUOTE_TOKEN,
        valid_to=int((datetime.utcnow() + timedelta(hours=2)).timestamp()),
    )


async def do_sell(token_swapper: TokenSwapper):
    return await create_limit_sell_order(
        sell_amount=AMOUNT_BEFORE_FEE,
        price=PRICE,
        swapper=token_swapper,
        quote_token=QUOTE_TOKEN,
        quote_token_decimals=QUOTE_TOKEN_DECIMALS,
        base_token=BASE_TOKEN,
        base_token_decimals=BASE_TOKEN_DECIMALS,
        valid_to=int((datetime.utcnow() + timedelta(hours=2)).timestamp()),
    )


async def main(auto_approve: bool = False):
    token_swapper = TokenSwapper(
        account=ACCOUNT,
        chain=CHAIN,
    )

    print("Price to trade at:", PRICE)

    if auto_approve or input("Create sell order? (y/n): ").lower() == "y":
        print(
            f"Amount to sell: {AMOUNT_BEFORE_FEE / (10**BASE_TOKEN_DECIMALS)} WETH for {AMOUNT_BEFORE_FEE / (10**QUOTE_TOKEN_DECIMALS) * PRICE} USDC"
        )
        sell_order = await do_sell(token_swapper)
        print(f"Created order: {sell_order.url}")
        print(f"Order details: {sell_order}")
    if auto_approve or input("Create buy order? (y/n): ").lower() == "y":
        print(
            f"Amount to buy: {AMOUNT_BEFORE_FEE / (10**BASE_TOKEN_DECIMALS)} WETH for {AMOUNT_BEFORE_FEE / (10**QUOTE_TOKEN_DECIMALS) * PRICE} USDC"
        )
        buy_order = await do_buy(token_swapper)
        print(f"Created order: {buy_order.url}")
        print(f"Order details: {buy_order}")


if __name__ == "__main__":
    asyncio.run(main(auto_approve=False))
