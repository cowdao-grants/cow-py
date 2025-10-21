# To run this test you will need to fill the .env file with the necessary variables (see .env.example).
# You will also need to have enough funds in you wallet of the sell token to create the order.
# The funds have to already be approved to the CoW Swap Vault Relayer

import os
import asyncio
from dotenv import load_dotenv
from web3 import Account, Web3
from web3.types import Wei
from cowdao_cowpy import TokenSwapper
from cowdao_cowpy.common.chains import Chain

SELL_TOKEN = Web3.to_checksum_address(
    "0xfFf9976782d46CC05630D1f6eBAb18b2324d6B14"
)  # WETH
BUY_TOKEN = Web3.to_checksum_address(
    "0xbe72E441BF55620febc26715db68d3494213D8Cb"
)  # USDC
SELL_AMOUNT_BEFORE_FEE = Wei(int(0.01 * 10**18))  # 0.01 WETH with 18 decimals
CHAIN = Chain.SEPOLIA

load_dotenv()

PRIVATE_KEY = os.getenv("TEST_PRIVATE_KEY")

if not PRIVATE_KEY:
    raise ValueError("Missing variables on .env file")

ACCOUNT = Account.from_key(PRIVATE_KEY)


def main():
    print("Swapping tokens...")
    print(f"Sell Token: {SELL_TOKEN}")
    print(f"Buy Token: {BUY_TOKEN}")
    print(f"Sell Amount: {SELL_AMOUNT_BEFORE_FEE}")

    token_swapper = TokenSwapper(chain=CHAIN, account=ACCOUNT)

    async def perform_swap_steps():
        await token_swapper.approve_relayer_if_needed(
            SELL_TOKEN, SELL_AMOUNT_BEFORE_FEE
        )
        order = await token_swapper.swap(
            amount=SELL_AMOUNT_BEFORE_FEE,
            sell_token=SELL_TOKEN,
            buy_token=BUY_TOKEN,
        )
        return order

    order = asyncio.run(perform_swap_steps())
    print("Created order:")
    print(f"     id:    {order.uid.root}")
    print(f"     url:   {order.url}")


if __name__ == "__main__":
    main()
