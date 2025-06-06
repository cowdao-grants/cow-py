# CoW Protocol Python SDK

[Help the herd 🐮](https://snapshot.org/#/cowgrants.eth/proposal/0x29bde0a0789a15f2255e11bdff088b4ffdf491729250dbe93b8b0776beb7f999)

## 🐄 Introduction

Welcome to the CoW Protocol Python SDK (cowdao_cowpy), a developer-friendly Python library for interacting with the CoW Protocol. This SDK provides tools for querying on-chain data, managing orders, and integrating with the CoW Protocol's smart contracts. Whether you're building a DeFi application, a solver, or just exploring the CoW Protocol, this SDK aims to make your development journey smoother and more enjoyable. 🚀

## 🐄 Features

- Querying CoW Protocol subgraph.
- Managing orders on the CoW Protocol.
- Interacting with CoW Protocol smart contracts.
- Encoding orders metadata and pinning to CID.
- Fetching and decoding blockchain data.

## 🐄 Installation

Get started by installing `cowdao_cowpy`:

```bash
pip install cowdao_cowpy
```

## 🐄 Getting Started

Here's a simple example to get your hooves dirty:

```python

from cowdao_cowpy.order_book.api import OrderBookApi, UID

# Initialize the OrderBookApi
order_book_api = OrderBookApi()

# Fetch and display orders
orders = order_book.get_order_by_uid(UID("0x..."))
print(orders)
```

## 🐄 Project Structure

- `common/`: Utilities and configurations, the backbone of the SDK.
- `contracts/`(TODO): A pasture of Smart contract ABIs for interaction.
- `order_book/`: Functions to wrangle orders on the CoW Protocol.
- `order_signing/`(TODO): Tools for signing and validating orders. Anything inside this module should use higher level modules, and the process of actually signing (ie. calling the web3 function to generate the signature, should be handled in contracts, not here).
- `subgraph/`: GraphQL client for querying CoW Protocol's Subgraph.
- `web3/`: Web3 providers for blockchain interactions.

## 🐄 How to Use

### Querying the Subgraph

Using the built-in GraphQL client, you can query the CoW Protocol's Subgraph to get real-time data on the CoW Protocol. You can query the Subgraph by using the `SubgraphClient` class and passing in the URL of the Subgraph.

```python
from cowdao_cowpy.subgraph.client import SubgraphClient
from cowdao_cowpy.subgraph.deployments import build_subgraph_url

url = build_subgraph_url() # Default network is Chain.SEPOLIA and env SubgraphEnvironment.PRODUCTION
client = SubgraphClient(url=url)

# Fetch the total supply of the CoW Protocol, defined in a query in cowdao_cowpy/subgraph/queries
totals = await client.totals()
print(totals) # Pydantic model, defined in cowdao_cowpy/subgraph/graphql_client/{query_name}.py
```

Or you can leverage `SubgraphClient` to use a custom query and get the results as JSON:

```python
from pprint import pprint
from cowdao_cowpy.subgraph.client import SubgraphClient
from cowdao_cowpy.subgraph.deployments import build_subgraph_url

url = build_subgraph_url() # Default network is Chain.SEPOLIA and env SubgraphEnvironment.PRODUCTION
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

Or you can leverage `SubgraphClient` to use a custom query and get the results as JSON:

```python
from pprint import pprint
from cowdao_cowpy.subgraph.client import SubgraphClient
from cowdao_cowpy.subgraph.deployments import build_subgraph_url

url = build_subgraph_url() # Default network is Chain.SEPOLIA and env SubgraphEnvironment.PRODUCTION
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

After making changes, make sure to run the appropriate code generation tasks and tests:

```bash
make codegen
make test
```

Integration Tests can be run by providing a private key for the E2E testing account. This is required to run the integration tests against the CoW Protocol's mainnet.

```bash
export E2E_GNOSIS_MAINNET_TESTING_EOA_PRIVATE_KEY=0x123...
poetry run pytest tests/ --with-slow --integration
```

## 🐄 Release Flow

```bash
tbump current-version
tbump NEW_VERSION
```


## 🐄 Need Help?

Got questions, bug reports, or feature requests? Open an issue in our [GitHub repository](https://github.com/cowdao-grants/cow-py/issues).

## 🐄 License

`cowdao_cowpy` is released under the GNU License. For more details, check out the [LICENSE](LICENSE) file.

---

Happy coding, and may the herd be with you! 🐄💻
