"""
Test the functionality of the token swapper module.
"""

from eth_account import Account
import pytest
from cowdao_cowpy import TokenSwapper
from cowdao_cowpy.common.chains import Chain
from cowdao_cowpy.order_book.generated.model import Address, OrderKind
from web3.types import Wei
import os


BUY_TOKEN = Address("0xbe72E441BF55620febc26715db68d3494213D8Cb")  # USDC
SELL_TOKEN = Address("0xfFf9976782d46CC05630D1f6eBAb18b2324d6B14")  # WETH
SELL_AMOUNT_BEFORE_FEE = Wei(500000000000000000)  # 50 USDC with 18 decimals

BUY_TOKEN_DECIMALS = 18
SELL_TOKEN_DECIMALS = 18


@pytest.fixture
def test_account():
    """Get a test account from environment variables."""
    private_key = os.getenv("TEST_PRIVATE_KEY")
    if not private_key:
        raise ValueError("Missing TEST_PRIVATE_KEY in environment variables")
    account = Account.from_key(private_key)
    return account


@pytest.fixture
def token_swapper(test_account):
    """Initialize and return a TokenSwapper instance."""

    chain = Chain.SEPOLIA

    return TokenSwapper(
        account=test_account,
        chain=chain,
    )


@pytest.mark.integration
def test_token_swapper_initialization(token_swapper):
    """Test that the TokenSwapper is initialized correctly."""
    assert token_swapper.chain == Chain.SEPOLIA
    assert token_swapper.account is not None


@pytest.mark.integration
@pytest.mark.asyncio
async def test_quote_sell(token_swapper):
    """Test getting a quote for a token swap."""
    quote = await token_swapper.get_quote(
        base_token=SELL_TOKEN,
        quote_token=BUY_TOKEN,
        amount=SELL_AMOUNT_BEFORE_FEE,
    )
    assert quote is not None
    assert quote.quote.sellToken.root == SELL_TOKEN.root.lower()
    assert quote.quote.buyToken.root == BUY_TOKEN.root.lower()
    assert int(quote.quote.sellAmount.root) == SELL_AMOUNT_BEFORE_FEE
    assert int(quote.quote.buyAmount.root) > 0
    price = await token_swapper.get_price_from_quote(quote)
    assert price > 0


@pytest.mark.integration
@pytest.mark.asyncio
async def test_quote_buy(token_swapper):
    """Test getting a quote for buying a specific amount of a token."""

    quote = await token_swapper.get_quote(
        base_token=SELL_TOKEN,
        quote_token=BUY_TOKEN,
        amount=SELL_AMOUNT_BEFORE_FEE,
        order_kind=OrderKind.buy,
    )
    assert quote is not None
    assert quote.quote.sellToken.root == BUY_TOKEN.root.lower()
    assert quote.quote.buyToken.root == SELL_TOKEN.root.lower()
    assert int(quote.quote.sellAmount.root) > 0
    assert int(quote.quote.buyAmount.root) == SELL_AMOUNT_BEFORE_FEE
    price = await token_swapper.get_price_from_quote(quote)
    assert price > 0
