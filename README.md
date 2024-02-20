# cow-py

CoW Protocol Python SDK

[Help the herd 🐮](https://snapshot.org/#/cowgrants.eth/proposal/0x29bde0a0789a15f2255e11bdff088b4ffdf491729250dbe93b8b0776beb7f999)

## 🐄 Introduction

Welcome to the CoW Protocol Python SDK (cow_py), a developer-friendly Python library for interacting with the CoW Protocol. This SDK provides tools for querying on-chain data, managing orders, and integrating with the CoW Protocol's smart contracts. Whether you're building a DeFi application, a solver, or just exploring the CoW Protocol, this SDK aims to make your development journey smoother and more enjoyable. 🚀

## 🐄 Features

- Querying CoW Protocol subgraphs.
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
# TODO: this code is aspirational, this API doesn't exist
from cow_py.order_book import OrderBook

# Initialize the OrderBook
order_book = OrderBook()

# Fetch and display orders
orders = order_book.get_orders()
print(orders)
```

## 🐄 Project Structure

- `common/`(WIP): Utilities and configurations, the backbone of the SDK.
- `contracts/`(TODO): A pasture of Smart contract ABIs for interaction.
- `order_book/`(TODO): Functions to wrangle orders on the CoW Protocol.
- `order_signing/`(TODO): Tools for signing and validating orders. Anything inside this module should use higher level modules, and the process of actually signing (ie. calling the web3 function to generate the signature, should be handled in contracts, not here).
- `subgraphs/`(WIP): GraphQL clients for querying CoW Protocol data.
- `web3/`: Web3 providers for blockchain interactions.

## 🐄 How to Use

### Querying the Subgraph (WIP)

```python
from cow_py.subgraphs.queries import TotalsQuery

totals_query = TotalsQuery()
totals = await totals_query.execute()
print(totals)
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
