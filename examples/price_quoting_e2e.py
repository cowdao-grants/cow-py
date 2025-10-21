import os

import asyncio
from dotenv import load_dotenv
from web3 import Account
from web3.types import Wei
from cowdao_cowpy.common.chains import Chain
from cowdao_cowpy.cow.swap import TokenSwapper
from cowdao_cowpy.order_book.generated.model import Address, OrderKind

QUOTE_TOKEN = Address("0xbe72E441BF55620febc26715db68d3494213D8Cb")  # USDC
BASE_TOKEN = Address("0xfFf9976782d46CC05630D1f6eBAb18b2324d6B14")  # WETH
SELL_AMOUNT_BEFORE_FEE = Wei(500000000000000000)  # 50 USDC with 18 decimals
CHAIN = Chain.SEPOLIA


SLIPPAGE_TOLERANCE = 0.0

load_dotenv()

PRIVATE_KEY = os.getenv("TEST_PRIVATE_KEY")

if not PRIVATE_KEY:
    raise ValueError("Missing variables on .env file")

ACCOUNT = Account.from_key(PRIVATE_KEY)


async def get_market_name(token_swapper: TokenSwapper):
    token_a = token_swapper.get_token_symbol(BASE_TOKEN)
    token_b = token_swapper.get_token_symbol(QUOTE_TOKEN)
    return await asyncio.gather(token_a, token_b)


async def get_quotes(token_swapper: TokenSwapper):
    sell_quote = token_swapper.get_quote(
        base_token=token_swapper.web3.to_checksum_address(BASE_TOKEN.root),
        quote_token=token_swapper.web3.to_checksum_address(QUOTE_TOKEN.root),
        amount=SELL_AMOUNT_BEFORE_FEE,
        order_kind=OrderKind.sell,
    )
    buy_quote = token_swapper.get_quote(
        base_token=token_swapper.web3.to_checksum_address(BASE_TOKEN.root),
        quote_token=token_swapper.web3.to_checksum_address(QUOTE_TOKEN.root),
        amount=SELL_AMOUNT_BEFORE_FEE,
        order_kind=OrderKind.buy,
    )
    return await asyncio.gather(sell_quote, buy_quote)


async def print_prices(sell_quote, buy_quote, token_swapper: TokenSwapper):
    sell_price, buy_price = await asyncio.gather(
        token_swapper.get_price_from_quote(sell_quote),
        token_swapper.get_price_from_quote(buy_quote),
    )
    print(f"Sell Price: {sell_price}")
    print(f"Buy Price: {buy_price}")


async def set_approvals(token_swapper: TokenSwapper):
    for token in [BASE_TOKEN, QUOTE_TOKEN]:
        await token_swapper.approve_relayer_if_needed(
            token_address=token_swapper.web3.to_checksum_address(token.root),
            amount=SELL_AMOUNT_BEFORE_FEE,
        )


async def main(auto_approve: bool = False):
    token_swapper = TokenSwapper(
        account=ACCOUNT,
        chain=CHAIN,
    )

    market = await get_market_name(token_swapper)
    market = f"{market[0]}/{market[1]}"
    print(f"Getting price quotes on market {market}...")

    # checking approvals
    await set_approvals(token_swapper)

    sell_quote, buy_quote = await get_quotes(token_swapper)

    await print_prices(sell_quote, buy_quote, token_swapper)

    if auto_approve or input("Do you want to create a sell order? (y/n): ") == "y":
        order = token_swapper.create_order(
            sell_token=token_swapper.web3.to_checksum_address(BASE_TOKEN.root),
            buy_token=token_swapper.web3.to_checksum_address(QUOTE_TOKEN.root),
            amount=SELL_AMOUNT_BEFORE_FEE,
            order_quote=sell_quote,
            slippage_tolerance=SLIPPAGE_TOLERANCE,
            valid_to=None,
            partially_fillable=False,
        )
        completed_order = await token_swapper.sign_and_post_order(order)
        print(completed_order)

    if auto_approve or input("Do you want to create a buy order? (y/n): ") == "y":
        order = token_swapper.create_order(
            sell_token=token_swapper.web3.to_checksum_address(QUOTE_TOKEN.root),
            buy_token=token_swapper.web3.to_checksum_address(BASE_TOKEN.root),
            amount=SELL_AMOUNT_BEFORE_FEE,
            order_quote=buy_quote,
            slippage_tolerance=SLIPPAGE_TOLERANCE,
            valid_to=None,
            partially_fillable=False,
        )
        completed_order = await token_swapper.sign_and_post_order(order)
        print(completed_order)


if __name__ == "__main__":
    asyncio.run(main())
