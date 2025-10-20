import asyncio
from datetime import datetime
from typing import cast

from eth_utils.address import to_checksum_address
from cowdao_cowpy.app_data.utils import DEFAULT_APP_DATA_HASH
from cowdao_cowpy.common.chains import Chain
from cowdao_cowpy.common.config import SupportedChainId
from cowdao_cowpy.common.constants import CowContractAddress
from cowdao_cowpy.contracts.domain import domain
from cowdao_cowpy.contracts.order import Order
from cowdao_cowpy.contracts.sign import (
    SigningScheme,
    PreSignSignature,
    Signature,
)
from cowdao_cowpy.contracts.sign import sign_order as _sign_order
from cowdao_cowpy.order_book.api import OrderBookApi
from cowdao_cowpy.order_book.config import Envs, OrderBookAPIConfigFactory
from web3.types import Wei
from cowdao_cowpy.order_book.generated.model import (
    UID,
    OrderCreation,
    OrderQuoteRequest,
    OrderQuoteResponse,
    OrderQuoteSide2,
    OrderQuoteSide3,
    OrderQuoteSideKindSell,
    OrderQuoteSideKindBuy,
    TokenAmount,
    OrderParameters,
    Address,
    AppDataHash,
    OrderKind,
)
from eth_account.signers.local import LocalAccount
from eth_account.types import TransactionDictType
from pydantic import BaseModel
from eth_typing.evm import ChecksumAddress
from web3 import AsyncWeb3
from web3.contract.async_contract import AsyncContract
from web3.providers.rpc import AsyncHTTPProvider


ERC20_ABI = [
    {
        "constant": False,
        "inputs": [
            {"name": "_spender", "type": "address"},
            {"name": "_value", "type": "uint256"},
        ],
        "name": "approve",
        "outputs": [{"name": "", "type": "bool"}],
        "payable": False,
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [
            {"name": "_owner", "type": "address"},
            {"name": "_spender", "type": "address"},
        ],
        "name": "allowance",
        "outputs": [{"name": "remaining", "type": "uint256"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
    },
    {
        "constant": True,
        "name": "decimals",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
    },
    {
        "constant": True,
        "name": "symbol",
        "outputs": [{"name": "symbol", "type": "string"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
    },
]


MAX_INT = 2**256 - 1


class CompletedOrder(BaseModel):
    uid: UID
    url: str


CHAIN_TO_EXPLORER = {
    SupportedChainId.MAINNET: "https://explorer.cow.fi/ethereum",
    SupportedChainId.ARBITRUM_ONE: "https://explorer.cow.fi/arb1",
    SupportedChainId.BASE: "https://explorer.cow.fi/base",
    SupportedChainId.GNOSIS_CHAIN: "https://explorer.cow.fi/gc",
    SupportedChainId.SEPOLIA: "https://explorer.cow.fi/sepolia",
}

CHAIN_TO_FREE_RPC = {
    SupportedChainId.MAINNET: "https://eth.drpc.org",
    SupportedChainId.ARBITRUM_ONE: "https://arb1.drpc.org",
    SupportedChainId.BASE: "https://base.drpc.org",
    SupportedChainId.GNOSIS_CHAIN: "https://gnosis.drpc.org",
    SupportedChainId.SEPOLIA: "https://0xrpc.io/sep",
}


class TokenSwapper:
    """
    A class-based interface for swapping tokens using the CoW Protocol.

    Note: `CowContractAddress.VAULT_RELAYER` needs to be approved to spend
    the sell token before calling swap methods.
    """

    def __init__(
        self,
        chain: Chain,
        account: LocalAccount,
        env: Envs = "prod",
        safe_address: ChecksumAddress | None = None,
        rpc_url: str | None = None,
    ):
        """
        Initialize the TokenSwapper.

        Args:
            chain: The blockchain to operate on
            account: The account to sign transactions with
            env: The environment (prod/staging/etc)
            safe_address: Optional Safe multisig address for pre-signed orders
        """
        self.chain = chain
        self.account = account
        self.env = env
        self.safe_address = safe_address
        self.chain_id = SupportedChainId(chain.value[0])
        self.order_book_api = OrderBookApi(
            OrderBookAPIConfigFactory.get_config(env, self.chain_id)
        )
        rpc_url = rpc_url or CHAIN_TO_FREE_RPC[self.chain_id]
        self.web3 = AsyncWeb3(AsyncHTTPProvider(rpc_url))
        self._token_decimals = {}

    async def approve_relayer_if_needed(
        self,
        token_address: ChecksumAddress,
        amount: int = MAX_INT,
    ) -> bool:
        """
        Approve the CoW Protocol Vault Relayer to spend the sell token.
        Args:
            amount: The amount to approve (default MAX_INT)
        Returns:
            bool: True if the approval transaction was successful, False otherwise.
        """
        token_contract: AsyncContract = self.web3.eth.contract(
            address=token_address,
            abi=ERC20_ABI,
        )
        if (
            await token_contract.functions.allowance(
                self.account.address, CowContractAddress.VAULT_RELAYER.value
            ).call()
            >= amount
        ):
            return True  # already approved
        print("Approving relayer to spend tokens...")
        nonce = await self.web3.eth.get_transaction_count(self.account.address)
        raw_tx = token_contract.functions.approve(
            CowContractAddress.VAULT_RELAYER.value,
            amount,
        )
        tx = await raw_tx.build_transaction(
            {
                "from": self.account.address,
                "nonce": nonce,
                "chainId": self.chain_id.value,
                "gas": 100000,
                "gasPrice": await self.web3.eth.gas_price,
            }
        )
        signed_tx = self.account.sign_transaction(cast(TransactionDictType, tx))
        tx_hash = await self.web3.eth.send_raw_transaction(signed_tx.raw_transaction)
        receipt = await self.web3.eth.wait_for_transaction_receipt(tx_hash)
        return receipt["status"] == 1  # status 1 means success

    async def get_token_decimals(self, token_address: Address) -> int:
        """
        Get the decimals of a token.

        Args:
            token_address: Address of the token

        Returns:
            int: Number of decimals
        """
        if token_address.root in self._token_decimals:
            return self._token_decimals[token_address]
        address = self.web3.to_checksum_address(token_address.root)
        token_contract: AsyncContract = self.web3.eth.contract(
            address=address,
            abi=ERC20_ABI,
        )
        decimals = await token_contract.functions.decimals().call()
        self._token_decimals[token_address.root] = decimals
        return decimals

    async def get_token_symbol(self, token_address: Address) -> str:
        """
        Get the symbol of a token.

        Args:
            token_address: Address of the token

        Returns:
            str: Token symbol
        """
        token_contract: AsyncContract = self.web3.eth.contract(
            address=self.web3.to_checksum_address(token_address.root),
            abi=ERC20_ABI,
        )
        symbol = await token_contract.functions.symbol().call()
        return symbol

    async def swap(
        self,
        amount: Wei,
        sell_token: ChecksumAddress,
        buy_token: ChecksumAddress,
        app_data: str = DEFAULT_APP_DATA_HASH,
        valid_to: int | None = None,
        slippage_tolerance: float = 0.005,
        partially_fillable: bool = False,
    ) -> CompletedOrder:
        """
        Execute a token swap.

        Args:
            amount: Amount of sell token to swap
            sell_token: Address of token to sell
            buy_token: Address of token to buy
            app_data: Application data hash
            valid_to: Optional expiration timestamp
            slippage_tolerance: Maximum allowed slippage (default 0.5%)
            partially_fillable: Whether the order can be partially filled

        Returns:
            CompletedOrder with UID and explorer URL
        """
        order_quote = await self.get_quote(
            base_token=sell_token,
            quote_token=buy_token,
            amount=amount,
            app_data=app_data,
        )

        order = self.create_order(
            sell_token=sell_token,
            buy_token=buy_token,
            amount=amount,
            order_quote=order_quote,
            app_data=app_data,
            valid_to=valid_to,
            slippage_tolerance=slippage_tolerance,
            partially_fillable=partially_fillable,
        )

        signature = self._sign_order(order)
        order_uid = await self._post_order(order, signature)
        order_link = self.order_book_api.get_order_link(order_uid)

        return CompletedOrder(uid=order_uid, url=order_link)

    async def get_quote(
        self,
        base_token: ChecksumAddress,
        quote_token: ChecksumAddress,
        amount: Wei,
        app_data: str = DEFAULT_APP_DATA_HASH,
        order_kind: OrderKind = OrderKind.sell,
    ) -> OrderQuoteResponse:
        """
        Get a quote from the order book API.
        For example: WETH/USDC
            base_token: WETH
            quote_token: USDC
        Allowing to specify whether we are selling base_token or buying base_token
        Args:
            base_token: Address of the base token
            quote_token: Address of the quote token
            amount: Amount of base token to sell or buy
            app_data: Application data hash
            order_kind: Whether the order is a sell or buy order
        Returns:
            OrderQuoteResponse from the order book API

        """
        order_quote_request = OrderQuoteRequest(
            sellToken=quote_token if order_kind == OrderKind.buy else base_token,
            buyToken=base_token if order_kind == OrderKind.buy else quote_token,
            from_=self.safe_address  # type: ignore
            if self.safe_address is not None
            else self.account._address,  # type: ignore
            appData=app_data,
        )
        if order_kind == OrderKind.sell:
            order_side = OrderQuoteSide2(
                kind=OrderQuoteSideKindSell.sell,
                sellAmountAfterFee=TokenAmount(str(amount)),
            )
        else:
            order_side = OrderQuoteSide3(
                kind=OrderQuoteSideKindBuy.buy,
                buyAmountAfterFee=TokenAmount(str(amount)),
            )

        return await self.order_book_api.post_quote(order_quote_request, order_side)

    async def get_price_from_quote(
        self,
        order_quote: OrderQuoteResponse,
    ) -> float:
        """Get the price from an order quote."""
        sell_amount = int(order_quote.quote.sellAmount.root)
        sell_decimal_fut = self.get_token_decimals(order_quote.quote.sellToken)
        buy_decimal_fut = self.get_token_decimals(order_quote.quote.buyToken)
        sell_decimals, buy_decimals = await asyncio.gather(
            sell_decimal_fut, buy_decimal_fut
        )
        buy_amount = int(order_quote.quote.buyAmount.root)
        if order_quote.quote.kind == OrderKind.sell:
            return (buy_amount / (10**buy_decimals)) / (
                sell_amount / (10**sell_decimals)
            )
        else:
            return (sell_amount / (10**sell_decimals)) / (
                buy_amount / (10**buy_decimals)
            )

    def create_order(
        self,
        sell_token: ChecksumAddress,
        buy_token: ChecksumAddress,
        amount: Wei,
        order_quote: OrderQuoteResponse,
        valid_to: int | None,
        slippage_tolerance: float,
        partially_fillable: bool,
        app_data: str = DEFAULT_APP_DATA_HASH,
    ) -> Order:
        """Create an order from quote parameters."""
        min_valid_to = (
            order_quote.quote.validTo
            if valid_to is None
            else min(order_quote.quote.validTo, valid_to)
        )

        receiver = (
            self.safe_address if self.safe_address is not None else self.account.address
        )

        return Order(
            sell_token=sell_token,
            buy_token=buy_token,
            receiver=receiver,
            valid_to=min_valid_to,
            app_data=app_data,
            sell_amount=str(order_quote.quote.sellAmount.root),
            buy_amount=str(
                int(int(order_quote.quote.buyAmount.root) * (1.0 - slippage_tolerance))
            ),
            fee_amount="0",
            kind=order_quote.quote.kind.value,
            sell_token_balance="erc20",
            buy_token_balance="erc20",
            partially_fillable=partially_fillable,
        )

    def _sign_order(self, order: Order) -> Signature:
        """Sign an order, or create a pre-sign signature for Safe."""
        if self.safe_address is not None:
            return PreSignSignature(
                scheme=SigningScheme.PRESIGN,
                data=self.safe_address,
            )

        order_domain = domain(
            chain=self.chain,
            verifying_contract=CowContractAddress.SETTLEMENT_CONTRACT.value,
        )
        return _sign_order(order_domain, order, self.account, SigningScheme.EIP712)

    async def _post_order(self, order: Order, signature: Signature) -> UID:
        """Post the signed order to the order book API."""
        from_address = (
            self.safe_address if self.safe_address is not None else self.account.address
        )

        order_creation = OrderCreation(
            from_=from_address,  # type: ignore
            sellToken=order.sellToken,
            buyToken=order.buyToken,
            sellAmount=str(order.sellAmount),
            feeAmount=str(order.feeAmount),
            buyAmount=str(order.buyAmount),
            validTo=order.validTo,
            kind=order.kind,
            partiallyFillable=order.partiallyFillable,
            appData=order.appData,
            signature=signature.to_string(),
            signingScheme=signature.scheme.name.lower(),
            receiver=order.receiver,
        )

        return await self.order_book_api.post_order(order_creation)

    async def create_limit_order(
        self,
        sell_token: Address,
        buy_token: Address,
        sell_amount: Wei,
        buy_amount: Wei,
        valid_to: int,
        app_data: str = DEFAULT_APP_DATA_HASH,
        partially_fillable: bool = False,
        order_kind: OrderKind = OrderKind.sell,
    ) -> CompletedOrder:
        """
        Create a limit order.

        Args:
            sell_token: Address of token to sell
            buy_token: Address of token to buy
            sell_amount: Amount of sell token
            buy_amount: Amount of buy token
            valid_to: Expiration timestamp
            app_data: Application data hash

        Returns:
            CompletedOrder with UID and explorer URL
        """
        quote = OrderParameters(
            sellToken=sell_token,
            buyToken=buy_token,
            receiver=None,
            sellAmount=TokenAmount(str(sell_amount)),
            buyAmount=TokenAmount(str(buy_amount)),
            validTo=valid_to,
            appData=AppDataHash(root=app_data),
            feeAmount=TokenAmount("0"),
            kind=order_kind,
            partiallyFillable=partially_fillable,
        )

        # examples=["1985-03-10T18:35:18.814523Z"],
        # expiration is validTo
        expiration = str(datetime.utcfromtimestamp(valid_to).isoformat() + "Z")
        order = self.create_order(
            sell_token=to_checksum_address(str(quote.sellToken.root)),
            buy_token=to_checksum_address(str(quote.buyToken.root)),
            amount=sell_amount,
            order_quote=OrderQuoteResponse(
                quote=quote,
                expiration=expiration,
                verified=False,  # type: ignore
            ),
            app_data=app_data,
            valid_to=valid_to,
            slippage_tolerance=0.0,  # No slippage for limit orders
            partially_fillable=partially_fillable,
        )

        return await self.sign_and_post_order(order)

    async def sign_and_post_order(
        self,
        order: Order,
    ) -> CompletedOrder:
        """Sign and post an order, returning a CompletedOrder."""
        signature = self._sign_order(order)
        order_uid = await self._post_order(order, signature)
        order_link = self.order_book_api.get_order_link(order_uid)

        return CompletedOrder(uid=order_uid, url=order_link)


# Backward compatibility: keep the original function
async def swap_tokens(
    amount: Wei,
    account: LocalAccount,
    chain: Chain,
    sell_token: ChecksumAddress,
    buy_token: ChecksumAddress,
    safe_address: ChecksumAddress | None = None,
    app_data: str = DEFAULT_APP_DATA_HASH,
    valid_to: int | None = None,
    env: Envs = "prod",
    slippage_tolerance: float = 0.005,
    partially_fillable: bool = False,
) -> CompletedOrder:
    """
    Swap tokens using the CoW Protocol. `CowContractAddress.VAULT_RELAYER` needs to be approved to spend the sell token before calling this function.

    This is a convenience wrapper around TokenSwapper for backward compatibility.
    """
    swapper = TokenSwapper(
        chain=chain,
        account=account,
        env=env,
        safe_address=safe_address,
    )

    return await swapper.swap(
        amount=amount,
        sell_token=sell_token,
        buy_token=buy_token,
        app_data=app_data,
        valid_to=valid_to,
        slippage_tolerance=slippage_tolerance,
        partially_fillable=partially_fillable,
    )


# limit order example
async def create_limit_sell_order(
    quote_token: Address,
    quote_token_decimals: int,
    base_token: Address,
    base_token_decimals: int,
    sell_amount: Wei,
    price: float,
    valid_to: int,
    swapper: TokenSwapper,
    app_data: str = DEFAULT_APP_DATA_HASH,
) -> CompletedOrder:
    """
    Create a limit order using the CoW Protocol. `CowContractAddress.VAULT_RELAYER` needs to be approved to spend the sell token before calling this function.


    Args:
        sell_token: Address of token to sell
        sell_token_decimals: Decimals of the sell token
        buy_token: Address of token to buy
        buy_token_decimals: Decimals of the buy token
        sell_amount: Amount of sell token
        price: Price of 1 unit of sell token in terms of buy token (e.g., if selling ETH for USDC, price is ETH price in USDC)
        valid_to: Expiration timestamp
        app_data: Application data hash
    Returns:
        CompletedOrder with UID and explorer URL
    """

    buy_amount = Wei(
        int(
            sell_amount / (10**base_token_decimals) * price * (10**quote_token_decimals)
        )
    )
    return await swapper.create_limit_order(
        sell_token=base_token,
        buy_token=quote_token,
        sell_amount=sell_amount,
        buy_amount=buy_amount,
        valid_to=valid_to,
        app_data=app_data,
        order_kind=OrderKind.sell,
    )


async def create_limit_buy_order(
    base_token: Address,
    base_token_decimals: int,
    quote_token: Address,
    quote_token_decimals: int,
    buy_amount: Wei,
    price: float,
    valid_to: int,
    swapper: TokenSwapper,
    app_data: str = DEFAULT_APP_DATA_HASH,
) -> CompletedOrder:
    """
    Create a limit buy order using the CoW Protocol. `CowContractAddress.VAULT_RELAYER` needs to be approved to spend the sell token before calling this function.


    Args:
        sell_token: Address of token to sell
        sell_token_decimals: Decimals of the sell token
        buy_token: Address of token to buy
        buy_token_decimals: Decimals of the buy token
        buy_amount: Amount of buy token
        price: Price of 1 unit of sell token in terms of buy token (e.g., if buying ETH with USDC, price is ETH price in USDC)
        app_data: Application data hash
        valid_to: Expiration timestamp
    Returns:
        CompletedOrder with UID and explorer URL
    """

    sell_amount = Wei(
        int(buy_amount / (10**base_token_decimals) * price * (10**quote_token_decimals))
    )
    return await swapper.create_limit_order(
        sell_token=quote_token,
        buy_token=base_token,
        sell_amount=sell_amount,
        buy_amount=buy_amount,
        valid_to=valid_to,
        app_data=app_data,
        order_kind=OrderKind.buy,
    )
