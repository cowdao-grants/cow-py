# CoW Protocol Python SDK

[Help the herd 🐮](https://snapshot.org/#/cowgrants.eth/proposal/0x29bde0a0789a15f2255e11bdff088b4ffdf491729250dbe93b8b0776beb7f999)

## 🐄 Introduction

Welcome to the CoW Protocol Python SDK (cow_py), a developer-friendly Python library for interacting with the CoW Protocol. This SDK provides tools for querying on-chain data, managing orders, and integrating with the CoW Protocol's smart contracts. Whether you're building a DeFi application, a solver, or just exploring the CoW Protocol, this SDK aims to make your development journey smoother and more enjoyable. 🚀

## 🐄 Features

- Querying the CoW Protocol subgraph.
- Managing orders on the CoW Protocol.
- Interacting with CoW Protocol smart contracts.
- Encoding orders metadata and pinning to CID.
- Fetching and decoding blockchain data.

## 🐄 Installation

Get started by installing `cow_py`:

```bash
pip install cow_py
```

## 🐄 Getting Started

Here's a simple example to get your hooves dirty:

```python

from cow_py.order_book.api import OrderBookApi, UID

# Initialize the OrderBookApi
order_book_api = OrderBookApi()

# Fetch and display orders
orders = order_book.get_order_by_uid(UID("0x..."))
print(orders)
```

## 🐄 Project Structure

- `common/`(WIP): Utilities and configurations, the backbone of the SDK.
- `contracts/`(TODO): A pasture of Smart contract ABIs for interaction.
- `order_book/`(TODO): Functions to wrangle orders on the CoW Protocol.
- `order_signing/`(TODO): Tools for signing and validating orders. Anything inside this module should use higher level modules, and the process of actually signing (ie. calling the web3 function to generate the signature, should be handled in contracts, not here).
- `subgraph/`(WIP): GraphQL client for querying CoW Protocol's subgraph.
- `web3/`: Web3 providers for blockchain interactions.

## 🐄 How to Use

### Querying the Subgraph

Using the built-in GraphQL client, you can query the CoW Protocol's Subgraph to get real-time data on the CoW Protocol. You can query the Subgraph by using the `SubgraphClient` class and passing in the URL of the Subgraph.

```python
from cow_py.subgraph.client import SubgraphClient

url = build_subgraph_url() # Default network is Chain.MAINNET and env SubgraphEnvironment.PRODUCTION
client = SubgraphClient(url=url)

# Fetch the total supply of the CoW Protocol, defined in a query in cow_py/subgraph/queries
totals = await client.totals()
print(totals) # Pydantic model, defined in cow_py/subgraph/graphql_client/{query_name}.py
```

Or you can leverage `SubgraphClient` to use a custom query and get the results as JSON:

```python
from pprint import pprint
from cow_py.subgraph.client import SubgraphClient

url = build_subgraph_url() # Default network is Chain.MAINNET and env SubgraphEnvironment.PRODUCTION
client = SubgraphClient(url=url)

response = await client.execute(query="""
            query LastDaysVolume($days: Int!) {
              dailyTotals(orderBy: timestamp, orderDirection: desc, first: $days) {
                timestamp
                volumeUsd
              }
            }
            """, variables=dict(days=2)
            )

data = client.get_data(response)
pprint(data)
```

### Signing an Order (TODO)

```python
from cow_py.order_signing import sign_order

# Example order details
order_details = {
    "sell_token": "0x...",
    "buy_token": "0x...",
    "sell_amount": 100000,
}

signed_order = sign_order(order_details, private_key="your_private_key")
print(signed_order)
```

## 🐄 Development

### 🐄 Tests

Run tests to ensure everything's working:

```bash
make test # or poetry run pytest
```

### 🐄 Formatting/Linting

Run the formatter and linter:

```bash
make format # or ruff check . --fix
make lint # or ruff format
```

### 🐄 Codegen

Generate the SDK from the CoW Protocol smart contracts, Subgraph, and Orderbook API:

```bash
make codegen
```


## 🐄 Contributing to the Herd

Interested in contributing? Here's how you can help:

```bash
git clone https://github.com/cowdao-grants/cow-py
cd cow-py
poetry install
```

Run tests to ensure everything's working:

```bash
poetry run pytest
```

## 🐄 Need Help?

Got questions, bug reports, or feature requests? Open an issue in our [GitHub repository](https://github.com/cowdao-grants/cow-py/issues).

## 🐄 License

`cow_py` is released under the GNU License. For more details, check out the [LICENSE](LICENSE) file.

---

Happy coding, and may the herd be with you! 🐄💻
