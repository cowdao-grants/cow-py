# To run this test you will need to fill the .env file with the necessary variables (see .env.example).
# You will also need to have enough funds in you wallet of the sell token to create the order.
# The funds have to already be approved to the CoW Swap Vault Relayer

import os
import asyncio
from dotenv import load_dotenv
from web3 import Account, Web3
from web3.types import Wei
from cow_py.cow.order_posting_e2e import swap_tokens
from cow_py.common.chains import Chain

BUY_TOKEN = Web3.to_checksum_address(
    "0xfFf9976782d46CC05630D1f6eBAb18b2324d6B14"
)  # WETH
SELL_TOKEN = Web3.to_checksum_address(
    "0xbe72E441BF55620febc26715db68d3494213D8Cb"
)  # USDC
SELL_AMOUNT_BEFORE_FEE = Wei(5000000000000000000)  # 50 USDC with 18 decimals
CHAIN = Chain.SEPOLIA

load_dotenv()

PRIVATE_KEY = os.getenv("PRIVATE_KEY")

if not PRIVATE_KEY:
    raise ValueError("Missing variables on .env file")

ACCOUNT = Account.from_key(PRIVATE_KEY)


if __name__ == "__main__":
    asyncio.run(
        swap_tokens(
            amount=SELL_AMOUNT_BEFORE_FEE,
            account=ACCOUNT,
            chain=CHAIN,
            sell_token=SELL_TOKEN,
            buy_token=BUY_TOKEN,
        )
    )
