from cowdao_cowpy.app_data.utils import DEFAULT_APP_DATA_HASH
from cowdao_cowpy.common.chains import Chain
from cowdao_cowpy.common.config import SupportedChainId
from cowdao_cowpy.common.constants import CowContractAddress
from cowdao_cowpy.contracts.domain import domain
from cowdao_cowpy.contracts.order import Order
from cowdao_cowpy.contracts.sign import (
    EcdsaSignature,
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
    OrderQuoteSide1,
    OrderQuoteSideKindSell,
    TokenAmount,
)
from eth_account.signers.local import LocalAccount
from pydantic import BaseModel
from eth_typing.evm import ChecksumAddress


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
    """
    chain_id = SupportedChainId(chain.value[0])
    order_book_api = OrderBookApi(OrderBookAPIConfigFactory.get_config(env, chain_id))

    order_quote_request = OrderQuoteRequest(
        sellToken=sell_token,
        buyToken=buy_token,
        from_=safe_address if safe_address is not None else account._address,  # type: ignore # pyright doesn't recognize `populate_by_name=True`.
        appData=app_data,
    )
    order_side = OrderQuoteSide1(
        kind=OrderQuoteSideKindSell.sell,
        sellAmountBeforeFee=TokenAmount(str(amount)),
    )

    order_quote = await get_order_quote(order_quote_request, order_side, order_book_api)

    min_valid_to = (
        order_quote.quote.validTo
        if valid_to is None
        else min(order_quote.quote.validTo, valid_to)
    )

    order = Order(
        sell_token=sell_token,
        buy_token=buy_token,
        receiver=safe_address if safe_address is not None else account.address,
        valid_to=min_valid_to,
        app_data=app_data,
        sell_amount=str(
            amount
        ),  # Since it is a sell order, the sellAmountBeforeFee is the same as the sellAmount.
        buy_amount=str(
            int(int(order_quote.quote.buyAmount.root) * (1.0 - slippage_tolerance))
        ),
        fee_amount="0",  # CoW Swap does not charge fees.
        kind=OrderQuoteSideKindSell.sell.value,
        sell_token_balance="erc20",
        buy_token_balance="erc20",
        partially_fillable=partially_fillable,
    )

    signature = (
        PreSignSignature(
            scheme=SigningScheme.PRESIGN,
            data=safe_address,
        )
        if safe_address is not None
        else sign_order(chain, account, order)
    )
    order_uid = await post_order(
        account, safe_address, order, signature, order_book_api
    )
    order_link = order_book_api.get_order_link(order_uid)
    return CompletedOrder(uid=order_uid, url=order_link)


async def get_order_quote(
    order_quote_request: OrderQuoteRequest,
    order_side: OrderQuoteSide1,
    order_book_api: OrderBookApi,
) -> OrderQuoteResponse:
    return await order_book_api.post_quote(order_quote_request, order_side)


def sign_order(chain: Chain, account: LocalAccount, order: Order) -> EcdsaSignature:
    order_domain = domain(
        chain=chain, verifying_contract=CowContractAddress.SETTLEMENT_CONTRACT.value
    )
    sig = _sign_order(order_domain, order, account, SigningScheme.EIP712)
    return sig


async def post_order(
    account: LocalAccount,
    safe_address: ChecksumAddress | None,
    order: Order,
    signature: Signature,
    order_book_api: OrderBookApi,
) -> UID:
    order_creation = OrderCreation(
        from_=safe_address if safe_address is not None else account.address,  # type: ignore # pyright doesn't recognize `populate_by_name=True`.
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
    return await order_book_api.post_order(order_creation)
