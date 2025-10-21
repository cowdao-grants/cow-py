# Orders

Functionality for creating and managing orders on the COW Protocol.

## Overview

The `orderbook_api` module provides functionality to create, manage, and interact with orders on the COW Protocol. It includes classes and methods for handling different types of orders, such as limit orders and market orders, as well as utilities for order management.



## Creating Orders

### Market Orders

Swapping tokens using market orders is straightforward. You can specify the amount of the token you want to sell, and the system will execute the swap at the best available market price.

```python
import os
import datetime
import asyncio
from dotenv import load_dotenv
from web3 import Account, Web3
from web3.types import Wei
from cowdao_cowpy.cow.swap import swap_tokens
from cowdao_cowpy.common.chains import Chain

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

SLIPPAGE_TOLERANCE = 0.005  # 0.5% slippage tolerance
VALID_TO = datetime.datetime.now().timestamp() + 3600  # Valid for 1 hour

ACCOUNT = Account.from_key(PRIVATE_KEY)

# Execute the swap
# This will create a market order to swap SELL_TOKEN for BUY_TOKEN
asyncio.run(
    swap_tokens(
        amount=SELL_AMOUNT_BEFORE_FEE,
        account=ACCOUNT,
        chain=CHAIN,
        sell_token=SELL_TOKEN,
        buy_token=BUY_TOKEN,
        slippage_tolerance=SLIPPAGE_TOLERANCE,
        valid_to=int(VALID_TO),
    )
)

```


### Limit Orders & Buy Orders

Limit orders allow you to specify the price at which you want to buy or sell a token. The order will only be executed if the market price reaches your specified limit price.

You can create a limit order by specifying the desired price and amount of tokens you want to buy or sell. The order will remain open until it is either filled or canceled.

Note: By default all orders are *technically* limit orders, with a minimum price specified as part of the order creation, however, allowed slippage is default set to 0.005 (0.5%), which means that the order will be executed at the best available price within that slippage tolerance. If you want to create a strict limit order, you can set the allowed slippage to 0.

We alternatively provide helper functions to create limit buy and limit sell orders directly, which do not allow for any slippage and allow you to specify the exact price you want to trade at.

```python
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

async def main(auto_approve: bool = False):
    token_swapper = TokenSwapper(
        account=ACCOUNT,
        chain=CHAIN,
    )

    print("Price to trade at:", PRICE)

    buy_order = await create_limit_buy_order(
        buy_amount=AMOUNT_BEFORE_FEE,
        price=PRICE,
        swapper=token_swapper,
        base_token=BASE_TOKEN,
        base_token_decimals=BASE_TOKEN_DECIMALS,
        quote_token_decimals=QUOTE_TOKEN_DECIMALS,
        quote_token=QUOTE_TOKEN,
        valid_to=int((datetime.utcnow() + timedelta(hours=2)).timestamp()),
    )
    print(f"Created order: {buy_order.url}")
    print(f"Order details: {buy_order}")


asyncio.run(main())

```

## Order Options

There are several different order options available when creating orders on the CoW Protocol.

This allows you to customize how your orders are executed and managed.

### Partial Fill Orders
Partial fill orders allow you to execute a portion of your order immediately while leaving the rest open for execution later. This is useful when you want to take advantage of current market conditions but are willing to wait for a better price on the remaining portion of your order.

```python
asyncio.run(
    swap_tokens(
        amount=SELL_AMOUNT_BEFORE_FEE,
        account=ACCOUNT,
        chain=CHAIN,
        sell_token=SELL_TOKEN,
        buy_token=BUY_TOKEN,
        partially_fillable=True,  # Allow partial fills
    )
)
```

## Fetching Order Details

To fetch details about a specific order, you can use the `get_order` method. This method retrieves information about an order based on its ID.

```python
from cowdao_cowpy.order_book.api import OrderBookApi, UID

# Initialize the OrderBookApi
order_book_api = OrderBookApi()

# Fetch and display individual order details
order = order_book_api.get_order_by_uid(UID("0x..."))
print(order)

# Fetch all orders for a specific user

orders = order_book_api.get_orders_by_owner("0x...")

# Display all orders
for order in orders:
    print(order)

```

## Canceling Orders
Todo: Add section on canceling orders

