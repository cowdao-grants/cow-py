# CoW Protocol Python SDK - Unofficial CoWSwap API Library

[![PyPI version](https://badge.fury.io/py/cowdao-cowpy.svg)](https://badge.fury.io/py/cowdao-cowpy)
[![Python 3.10+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![CI](https://github.com/cowdao-grants/cow-py/actions/workflows/ci.yml/badge.svg)](https://github.com/cowdao-grants/cow-py/actions/workflows/ci.yml)
[![MkDocs Deploy](https://github.com/cowdao-grants/cow-py/actions/workflows/pages.yaml/badge.svg)](https://github.com/cowdao-grants/cow-py/actions/workflows/pages.yaml)

[Help the herd 🐮](https://snapshot.org/#/cowgrants.eth/proposal/0x29bde0a0789a15f2255e11bdff088b4ffdf491729250dbe93b8b0776beb7f999)

## Comprehensive Python SDK for CoWSwap and CoW Protocol Integration

Welcome to the CoW Protocol Python SDK (`cowdao_cowpy`), a developer-friendly Python library for interacting with CoWSwap and the CoW Protocol. This SDK provides tools for querying on-chain data, managing orders, and integrating with the CoW Protocol's smart contracts. Whether you're building a DeFi application, a trading bot, a solver, or just exploring the CoW Protocol, this SDK aims to make your development journey smoother and more enjoyable. 🚀

### Keywords
`cowswap python`, `cow protocol sdk`, `cowswap api`, `cow swap python library`, `decentralized exchange python`, `dex aggregator python`, `ethereum trading python`, `mev protection python`, `intent-based trading`, `batch auction dex`, `web3 python`, `defi python sdk`

## 📚 Documentation
For detailed documentation on how to use the CoW Protocol Python SDK, please visit our [documentation site](https://cowdao-grants.github.io/cow-py/).

## 🐄 What is CoW Protocol / CoWSwap?

CoW Protocol (Coincidence of Wants) powers CoWSwap, a decentralized exchange (DEX) aggregator that protects traders from MEV (Maximal Extractable Value) through batch auctions and intent-based trading. This Python SDK enables developers to:

- **Trade on CoWSwap programmatically** - Execute swaps with MEV protection
- **Build trading bots** - Automate trading strategies on Ethereum and Gnosis Chain
- **Query CoW Protocol data** - Access order history, trading volumes, and market data via Subgraph
- **Integrate CoWSwap into applications** - Add CoW Protocol functionality to your DeFi projects
- **Create solvers** - Build custom order matching solutions

## 🐄 Features

- Querying CoW Protocol subgraph for trading data and analytics
- Managing orders on the CoW Protocol (create, fetch, cancel)
- Interacting with CoW Protocol smart contracts
- Encoding orders metadata and pinning to CID
- Fetching and decoding blockchain data
- Full Python type hints and async/await support

## 🚀 Key Features for CoWSwap Integration

### DEX Aggregation & MEV Protection
- Execute trades across multiple DEXs with best price execution
- Built-in MEV protection through CoW Protocol's batch auction mechanism
- Gasless trading - pay fees in sell tokens

### Python-First Development Experience
- **Type-safe** - Full type hints and Pydantic models throughout
- **Async/await** - Native asyncio support for high-performance applications
- **Web3.py integration** - Seamless Ethereum and Gnosis Chain interaction
- **GraphQL client** - Query CoW Protocol Subgraph efficiently

### Multi-Chain Support
- **Ethereum Mainnet** - Trade on CoWSwap with ETH and ERC20 tokens
- **Gnosis Chain** - Low-cost trading with xDai
- **Sepolia Testnet** - Test your CoWSwap integration safely
- **Arbitrum_One** - Layer 2 support for faster transactions
- **Avalanche** - Access CoW Protocol on Avalanche network
- **Polygon** - Trade on CoW Protocol via Polygon network
- **Base** - Interact with CoW Protocol on Base network
- **Lens** - Utilize CoW Protocol on Lens network
- **BNB** - Engage with CoW Protocol on BNB Chain

## 🐄 Installation

Get started by installing `cowdao_cowpy` via pip:
```bash
pip install cowdao_cowpy
```

PyPI Package: [https://pypi.org/project/cowdao-cowpy/](https://pypi.org/project/cowdao-cowpy/)

## 🐄 Getting Started


### Creating and Executing a Swap Order

Here's how to create and execute a token swap on CoWSwap using Python:
```python
import os
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
if not PRIVATE_KEY:
    raise ValueError("Missing variables on .env file")

ACCOUNT = Account.from_key(PRIVATE_KEY)

asyncio.run(
    swap_tokens(
        amount=SELL_AMOUNT_BEFORE_FEE,
        account=ACCOUNT,
        chain=CHAIN,
        sell_token=SELL_TOKEN,
        buy_token=BUY_TOKEN,
    )
)
```

### Simple Example: Fetching Orders

Here's a simple example of fetching orders to get your hooves dirty:
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
- `contracts/`: A pasture of Smart contract ABIs for interaction.
- `order_book/`: Functions to wrangle orders on the CoW Protocol.
- `order_signing/`: Tools for signing and validating orders. Anything inside this module should use higher level modules, and the process of actually signing (ie. calling the web3 function to generate the signature, should be handled in contracts, not here).
- `subgraph/`: GraphQL client for querying CoW Protocol's Subgraph.
- `web3/`: Web3 providers for blockchain interactions.

## 🐄 How to Use

### Querying the CoW Protocol Subgraph

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

## 🐄 Development

For developers looking to contribute or extend the SDK, here's how to set up your development environment:

### 🐄 Setup

Clone the repository and install the dependencies:
```bash
git clone git@github.com:cowdao-grants/cow-py.git
cd cow-py
make install # or poetry install
```

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

## 📚 Additional Resources

- **CoW Protocol Documentation**: [https://docs.cow.fi/](https://docs.cow.fi/)
- **CoWSwap Interface**: [https://swap.cow.fi/](https://swap.cow.fi/)
- **CoW Protocol API Docs**: [https://api.cow.fi/docs](https://api.cow.fi/docs)
- **GitHub Repository**: [https://github.com/cowdao-grants/cow-py](https://github.com/cowdao-grants/cow-py)

## 🐄 Need Help?

Got questions, bug reports, or feature requests? Open an issue in our [GitHub repository](https://github.com/cowdao-grants/cow-py/issues).

Alternatively, you can join our community on [Discord](https://discord.gg/cowprotocol) or [Twitter](https://x.com/CoWSwap) to connect with other developers and get support.

## 🐄 License

`cowdao_cowpy` is released under the GNU License. For more details, check out the [LICENSE](LICENSE) file.

## 🔍 SEO Keywords

Python SDK for: CoWSwap, CoW Protocol, DEX trading, Ethereum trading bot, DeFi development, order book API, intent-based trading, batch auctions, MEV protection, decentralized exchange integration, Web3 automation, cryptocurrency trading, Gnosis Chain, ERC20 tokens, smart contract interaction

---

Happy coding, and may the herd be with you! 🐄💻

**Star ⭐ this repository to support CoW Protocol development!**