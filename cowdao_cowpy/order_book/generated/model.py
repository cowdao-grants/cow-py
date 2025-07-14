from __future__ import annotations
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from cowdao_cowpy.order_book.base import BaseModel
from pydantic import Field, RootModel, confloat


class TransactionHash(RootModel[str]):
    root: str = Field(
        ...,
        description="32 byte digest encoded as a hex with `0x` prefix.",
        examples=["0xd51f28edffcaaa76be4a22f6375ad289272c037f3cc072345676e88d92ced8b5"],
    )


class Address(RootModel[str]):
    root: str = Field(
        ...,
        description="20 byte Ethereum address encoded as a hex with `0x` prefix.",
        examples=["0x6810e776880c02933d47db1b9fc05908e5386b96"],
    )


class AppData(RootModel[str]):
    root: str = Field(
        ...,
        description="The string encoding of a JSON object representing some `appData`. The\nformat of the JSON expected in the `appData` field is defined\n[here](https://github.com/cowprotocol/app-data).\n",
        examples=['{"version":"0.9.0","metadata":{}}'],
    )


class AppDataHash(RootModel[str]):
    root: str = Field(
        ...,
        description="32 bytes encoded as hex with `0x` prefix.\nIt's expected to be the hash of the stringified JSON object representing the `appData`.\n",
        examples=["0x0000000000000000000000000000000000000000000000000000000000000000"],
    )


class AppDataObject(BaseModel):
    fullAppData: Optional[AppData] = None


class BigUint(RootModel[str]):
    root: str = Field(
        ...,
        description="A big unsigned integer encoded in decimal.",
        examples=["1234567890"],
    )


class CallData(RootModel[str]):
    root: str = Field(
        ...,
        description="Some `calldata` sent to a contract in a transaction encoded as a hex with `0x` prefix.",
        examples=["0xca11da7a"],
    )


class TokenAmount(RootModel[str]):
    root: str = Field(
        ...,
        description="Amount of a token. `uint256` encoded in decimal.",
        examples=["1234567890"],
    )


class PlacementError(Enum):
    QuoteNotFound = "QuoteNotFound"
    ValidToTooFarInFuture = "ValidToTooFarInFuture"
    PreValidationError = "PreValidationError"


class OnchainOrderData(BaseModel):
    sender: Address = Field(
        ...,
        description="If orders are placed as on-chain orders, the owner of the order might be a smart contract, but not the user placing the order. The actual user will be provided in this field.\n",
    )
    placementError: Optional[PlacementError] = Field(
        None,
        description="Describes the error, if the order placement was not successful. This could happen, for example, if the `validTo` is too high, or no valid quote was found or generated.\n",
    )


class EthflowData(BaseModel):
    refundTxHash: Optional[TransactionHash] = Field(
        None,
        description="Specifies in which transaction the order was refunded. If\nthis field is null the order was not yet refunded.\n",
    )
    userValidTo: int = Field(
        ...,
        description="Describes the `validTo` of an order ethflow order.\n\n**NOTE**: For ethflow orders, the `validTo` encoded in the smart\ncontract is `type(uint256).max`.\n",
    )


class OrderKind(Enum):
    buy = "buy"
    sell = "sell"


class OrderClass(Enum):
    market = "market"
    limit = "limit"
    liquidity = "liquidity"


class SellTokenSource(Enum):
    erc20 = "erc20"
    internal = "internal"
    external = "external"


class BuyTokenDestination(Enum):
    erc20 = "erc20"
    internal = "internal"


class PriceQuality(Enum):
    fast = "fast"
    optimal = "optimal"
    verified = "verified"


class OrderStatus(Enum):
    presignaturePending = "presignaturePending"
    open = "open"
    fulfilled = "fulfilled"
    cancelled = "cancelled"
    expired = "expired"


class ExecutedAmounts(BaseModel):
    sell: BigUint
    buy: BigUint


class Type(Enum):
    open = "open"
    scheduled = "scheduled"
    active = "active"
    solved = "solved"
    executing = "executing"
    traded = "traded"
    cancelled = "cancelled"


class ValueItem(BaseModel):
    solver: str = Field(..., description="Name of the solver.")
    executedAmounts: Optional[ExecutedAmounts] = None


class CompetitionOrderStatus(BaseModel):
    type: Type
    value: Optional[List[ValueItem]] = Field(
        None,
        description="A list of solvers who participated in the latest competition, sorted\nby score in ascending order, where the last element is the winner.\n\nThe presence of executed amounts defines whether the solver provided\na solution for the desired order.",
    )


class AuctionPrices(RootModel[Optional[Dict[str, BigUint]]]):
    root: Optional[Dict[str, BigUint]] = None


class UID(RootModel[str]):
    root: str = Field(
        ...,
        description="Unique identifier for the order: 56 bytes encoded as hex with `0x`\nprefix.\n\nBytes 0..32 are the order digest, bytes 30..52 the owner address and\nbytes 52..56 the expiry (`validTo`) as a `uint32` unix epoch timestamp.",
        examples=[
            "0xff2e2e54d178997f173266817c1e9ed6fee1a1aae4b43971c53b543cffcc2969845c6f5599fbb25dbdd1b9b013daf85c03f3c63763e4bc4a"
        ],
    )


class SigningScheme(Enum):
    eip712 = "eip712"
    ethsign = "ethsign"
    presign = "presign"
    eip1271 = "eip1271"


class EcdsaSigningScheme(Enum):
    eip712 = "eip712"
    ethsign = "ethsign"


class EcdsaSignature(RootModel[str]):
    root: str = Field(
        ...,
        description="65 bytes encoded as hex with `0x` prefix. `r || s || v` from the spec.",
        examples=[
            "0x0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
        ],
    )


class PreSignature(RootModel[str]):
    root: str = Field(
        ...,
        description='Empty signature bytes. Used for "presign" signatures.',
        examples=["0x"],
    )


class ErrorType(Enum):
    DuplicatedOrder = "DuplicatedOrder"
    QuoteNotFound = "QuoteNotFound"
    QuoteNotVerified = "QuoteNotVerified"
    InvalidQuote = "InvalidQuote"
    MissingFrom = "MissingFrom"
    WrongOwner = "WrongOwner"
    InvalidEip1271Signature = "InvalidEip1271Signature"
    InsufficientBalance = "InsufficientBalance"
    InsufficientAllowance = "InsufficientAllowance"
    InvalidSignature = "InvalidSignature"
    SellAmountOverflow = "SellAmountOverflow"
    TransferSimulationFailed = "TransferSimulationFailed"
    ZeroAmount = "ZeroAmount"
    IncompatibleSigningScheme = "IncompatibleSigningScheme"
    TooManyLimitOrders = "TooManyLimitOrders"
    TooMuchGas = "TooMuchGas"
    UnsupportedBuyTokenDestination = "UnsupportedBuyTokenDestination"
    UnsupportedSellTokenSource = "UnsupportedSellTokenSource"
    UnsupportedOrderType = "UnsupportedOrderType"
    InsufficientValidTo = "InsufficientValidTo"
    ExcessiveValidTo = "ExcessiveValidTo"
    InvalidNativeSellToken = "InvalidNativeSellToken"
    SameBuyAndSellToken = "SameBuyAndSellToken"
    UnsupportedToken = "UnsupportedToken"
    InvalidAppData = "InvalidAppData"
    AppDataHashMismatch = "AppDataHashMismatch"
    AppdataFromMismatch = "AppdataFromMismatch"
    OldOrderActivelyBidOn = "OldOrderActivelyBidOn"


class OrderPostError(BaseModel):
    errorType: ErrorType
    description: str


class ErrorType1(Enum):
    InvalidSignature = "InvalidSignature"
    WrongOwner = "WrongOwner"
    OrderNotFound = "OrderNotFound"
    AlreadyCancelled = "AlreadyCancelled"
    OrderFullyExecuted = "OrderFullyExecuted"
    OrderExpired = "OrderExpired"
    OnChainOrder = "OnChainOrder"


class OrderCancellationError(BaseModel):
    errorType: ErrorType1
    description: str


class ErrorType2(Enum):
    QuoteNotVerified = "QuoteNotVerified"
    UnsupportedToken = "UnsupportedToken"
    ZeroAmount = "ZeroAmount"
    UnsupportedOrderType = "UnsupportedOrderType"


class PriceEstimationError(BaseModel):
    errorType: ErrorType2
    description: str


class OrderQuoteSideKindSell(Enum):
    sell = "sell"


class OrderQuoteSideKindBuy(Enum):
    buy = "buy"


class OrderQuoteValidity1(BaseModel):
    validTo: Optional[int] = Field(
        None, description="Unix timestamp (`uint32`) until which the order is valid."
    )


class OrderQuoteValidity2(BaseModel):
    validFor: Optional[int] = Field(
        None,
        description="Number (`uint32`) of seconds that the order should be valid for.",
    )


class OrderQuoteValidity(RootModel[Union[OrderQuoteValidity1, OrderQuoteValidity2]]):
    root: Union[OrderQuoteValidity1, OrderQuoteValidity2] = Field(
        ..., description="The validity for the order."
    )


class Order1(BaseModel):
    id: Optional[UID] = None
    sellAmount: Optional[BigUint] = None
    buyAmount: Optional[BigUint] = None


class SolverSettlement(BaseModel):
    ranking: Optional[float] = Field(
        None,
        description="Which position the solution achieved in the total ranking of the competition.",
    )
    solverAddress: Optional[str] = Field(
        None,
        description="The address used by the solver to execute the settlement on-chain.\n\nThis field is missing for old settlements, the zero address has been\nused instead.",
    )
    score: Optional[BigUint] = Field(
        None,
        description="The score of the current auction as defined in [CIP-20](https://snapshot.org/#/cow.eth/proposal/0x2d3f9bd1ea72dca84b03e97dda3efc1f4a42a772c54bd2037e8b62e7d09a491f).\n",
    )
    referenceScore: Optional[BigUint] = Field(
        None,
        description="The reference score as defined in [CIP-67](https://forum.cow.fi/t/cip-67-moving-from-batch-auction-to-the-fair-combinatorial-auction/2967) (if available).\n",
    )
    txHash: Optional[TransactionHash] = Field(
        None,
        description="Transaction in which the solution was executed onchain (if available).\n",
    )
    clearingPrices: Optional[Dict[str, BigUint]] = Field(
        None,
        description="The prices of tokens for settled user orders as passed to the settlement contract.\n",
    )
    orders: Optional[List[Order1]] = Field(None, description="Touched orders.")
    isWinner: Optional[bool] = Field(
        None,
        description="whether the solution is a winner (received the right to get executed) or not",
    )
    filteredOut: Optional[bool] = Field(
        None,
        description="whether the solution was filtered out according to the rules of [CIP-67](https://forum.cow.fi/t/cip-67-moving-from-batch-auction-to-the-fair-combinatorial-auction/2967).",
    )


class NativePriceResponse(BaseModel):
    price: Optional[float] = Field(None, description="Estimated price of the token.")


class TotalSurplus(BaseModel):
    totalSurplus: Optional[str] = Field(None, description="The total surplus.")


class InteractionData(BaseModel):
    target: Optional[Address] = None
    value: Optional[TokenAmount] = None
    call_data: Optional[List[CallData]] = Field(
        None, description="The call data to be used for the interaction."
    )


class Quote(BaseModel):
    sellAmount: Optional[TokenAmount] = Field(
        None, description="The amount of the sell token."
    )
    buyAmount: Optional[TokenAmount] = Field(
        None, description="The amount of the buy token."
    )
    fee: Optional[TokenAmount] = Field(
        None,
        description="The amount that needs to be paid, denominated in the sell token.",
    )


class Surplus(BaseModel):
    factor: confloat(ge=0.0, lt=1.0)
    maxVolumeFactor: confloat(ge=0.0, lt=1.0)


class Volume(BaseModel):
    factor: confloat(ge=0.0, lt=1.0)


class PriceImprovement(BaseModel):
    factor: confloat(ge=0.0, lt=1.0)
    maxVolumeFactor: confloat(ge=0.0, lt=1.0)
    quote: Quote = Field(..., description="The best quote received.")


class FeePolicy(RootModel[Union[Surplus, Volume, PriceImprovement]]):
    root: Union[Surplus, Volume, PriceImprovement] = Field(
        ..., description="Defines the ways to calculate the protocol fee."
    )


class ExecutedProtocolFee(BaseModel):
    policy: Optional[FeePolicy] = None
    amount: Optional[TokenAmount] = None
    token: Optional[Address] = None


class OrderParameters(BaseModel):
    sellToken: Address = Field(..., description="ERC-20 token to be sold.")
    buyToken: Address = Field(..., description="ERC-20 token to be bought.")
    receiver: Optional[Address] = Field(
        None,
        description="An optional Ethereum address to receive the proceeds of the trade instead of the owner (i.e. the order signer).\n",
    )
    sellAmount: TokenAmount = Field(
        ..., description="Amount of `sellToken` to be sold in atoms."
    )
    buyAmount: TokenAmount = Field(
        ..., description="Amount of `buyToken` to be bought in atoms."
    )
    validTo: int = Field(
        ..., description="Unix timestamp (`uint32`) until which the order is valid."
    )
    appData: AppDataHash
    feeAmount: TokenAmount = Field(
        ...,
        description="sellAmount in atoms to cover network fees. Needs to be zero (and incorporated into the limit price) when placing the order",
    )
    kind: OrderKind = Field(..., description="The kind is either a buy or sell order.")
    partiallyFillable: bool = Field(
        ..., description="Is the order fill-or-kill or partially fillable?"
    )
    sellTokenBalance: Optional[SellTokenSource] = "erc20"
    buyTokenBalance: Optional[BuyTokenDestination] = "erc20"
    signingScheme: Optional[SigningScheme] = "eip712"


class OrderMetaData(BaseModel):
    creationDate: str = Field(
        ...,
        description="Creation time of the order. Encoded as ISO 8601 UTC.",
        examples=["2020-12-03T18:35:18.814523Z"],
    )
    class_: OrderClass = Field(..., alias="class")
    owner: Address
    uid: UID
    availableBalance: Optional[TokenAmount] = Field(
        None,
        description="Unused field that is currently always set to `null` and will be removed in the future.\n",
    )
    executedSellAmount: BigUint = Field(
        ...,
        description="The total amount of `sellToken` that has been transferred from the user for this order so far.\n",
    )
    executedSellAmountBeforeFees: BigUint = Field(
        ...,
        description="The total amount of `sellToken` that has been transferred from the user for this order so far minus tokens that were transferred as part of the signed `fee` of the order. This is only relevant for old orders because now all orders have a signed `fee` of 0 and solvers compute an appropriate fee dynamically at the time of the order execution.\n",
    )
    executedBuyAmount: BigUint = Field(
        ...,
        description="The total amount of `buyToken` that has been executed for this order.\n",
    )
    executedFeeAmount: BigUint = Field(
        ...,
        description="[DEPRECATED] The total amount of the user signed `fee` that have been executed for this order. This value is only non-negative for very old orders.\n",
    )
    invalidated: bool = Field(..., description="Has this order been invalidated?")
    status: OrderStatus = Field(..., description="Order status.")
    isLiquidityOrder: Optional[bool] = Field(
        None,
        description="Liquidity orders are functionally the same as normal smart contract\norders but are not placed with the intent of actively getting\ntraded. Instead they facilitate the trade of normal orders by\nallowing them to be matched against liquidity orders which uses less\ngas and can have better prices than external liquidity.\n\nAs such liquidity orders will only be used in order to improve\nsettlement of normal orders. They should not be expected to be\ntraded otherwise and should not expect to get surplus.",
    )
    ethflowData: Optional[EthflowData] = None
    onchainUser: Optional[Address] = Field(
        None,
        description="This represents the actual trader of an on-chain order.\n### ethflow orders\nIn this case, the `owner` would be the `EthFlow` contract and *not* the actual trader.\n",
    )
    onchainOrderData: Optional[OnchainOrderData] = Field(
        None,
        description="There is some data only available for orders that are placed on-chain. This data can be found in this object.\n",
    )
    executedFee: Optional[BigUint] = Field(
        None,
        description="Total fee charged for execution of the order. Contains network fee and protocol fees. This takes into account the historic static fee signed by the user and the new dynamic fee computed by solvers.\n",
    )
    executedFeeToken: Optional[Address] = Field(
        None, description="Token the executed fee was captured in."
    )
    fullAppData: Optional[str] = Field(
        None,
        description="Full `appData`, which the contract-level `appData` is a hash of. See `OrderCreation` for more information.\n",
    )


class CompetitionAuction(BaseModel):
    orders: Optional[List[UID]] = Field(
        None, description="The UIDs of the orders included in the auction.\n"
    )
    prices: Optional[AuctionPrices] = None


class OrderCancellations(BaseModel):
    orderUids: Optional[List[UID]] = Field(
        None, description="UIDs of orders to cancel."
    )
    signature: EcdsaSignature = Field(
        ..., description="`OrderCancellation` signed by the owner."
    )
    signingScheme: EcdsaSigningScheme


class OrderCancellation(BaseModel):
    signature: EcdsaSignature = Field(
        ..., description="OrderCancellation signed by owner"
    )
    signingScheme: EcdsaSigningScheme


class Trade(BaseModel):
    blockNumber: int = Field(..., description="Block in which trade occurred.")
    logIndex: int = Field(
        ..., description="Index in which transaction was included in block."
    )
    orderUid: UID = Field(..., description="UID of the order matched by this trade.")
    owner: Address = Field(..., description="Address of trader.")
    sellToken: Address = Field(..., description="Address of token sold.")
    buyToken: Address = Field(..., description="Address of token bought.")
    sellAmount: TokenAmount = Field(
        ...,
        description="Total amount of `sellToken` that has been executed for this trade (including fees).",
    )
    sellAmountBeforeFees: BigUint = Field(
        ...,
        description="The total amount of `sellToken` that has been executed for this order without fees.",
    )
    buyAmount: TokenAmount = Field(
        ..., description="Total amount of `buyToken` received in this trade."
    )
    txHash: Optional[TransactionHash] = Field(
        None,
        description="Transaction hash of the corresponding settlement transaction containing the trade (if available).",
    )
    executedProtocolFees: Optional[List[ExecutedProtocolFee]] = Field(
        None,
        description="Executed protocol fees for this trade, together with the fee policies used. Listed in the order they got applied.\n",
    )


class Signature(RootModel[Union[EcdsaSignature, PreSignature]]):
    root: Union[EcdsaSignature, PreSignature] = Field(..., description="A signature.")


class OrderQuoteSide1(BaseModel):
    kind: OrderQuoteSideKindSell
    sellAmountBeforeFee: TokenAmount = Field(
        ...,
        description="The total amount that is available for the order. From this value, the fee is deducted and the buy amount is calculated.\n",
    )


class OrderQuoteSide2(BaseModel):
    kind: OrderQuoteSideKindSell
    sellAmountAfterFee: TokenAmount = Field(
        ..., description="The `sellAmount` for the order."
    )


class OrderQuoteSide3(BaseModel):
    kind: OrderQuoteSideKindBuy
    buyAmountAfterFee: TokenAmount = Field(
        ..., description="The `buyAmount` for the order."
    )


class OrderQuoteSide(
    RootModel[Union[OrderQuoteSide1, OrderQuoteSide2, OrderQuoteSide3]]
):
    root: Union[OrderQuoteSide1, OrderQuoteSide2, OrderQuoteSide3] = Field(
        ..., description="The buy or sell side when quoting an order."
    )


class OrderQuoteRequest(BaseModel):
    sellToken: Address = Field(..., description="ERC-20 token to be sold")
    buyToken: Address = Field(..., description="ERC-20 token to be bought")
    receiver: Optional[Address] = Field(
        None,
        description="An optional address to receive the proceeds of the trade instead of the\n`owner` (i.e. the order signer).\n",
    )
    appData: Optional[Union[AppData, AppDataHash]] = Field(
        None,
        description="AppData which will be assigned to the order.\n\nExpects either a string JSON doc as defined on\n[AppData](https://github.com/cowprotocol/app-data) or a hex\nencoded string for backwards compatibility.\n\nWhen the first format is used, it's possible to provide the\nderived appDataHash field.",
    )
    appDataHash: Optional[AppDataHash] = Field(
        None,
        description="The hash of the stringified JSON appData doc.\n\nIf present, `appData` field must be set with the aforementioned\ndata where this hash is derived from.\n\nIn case they differ, the call will fail.",
    )
    sellTokenBalance: Optional[SellTokenSource] = "erc20"
    buyTokenBalance: Optional[BuyTokenDestination] = "erc20"
    from_: Address = Field(..., alias="from")
    priceQuality: Optional[PriceQuality] = "verified"
    signingScheme: Optional[SigningScheme] = "eip712"
    onchainOrder: Optional[Any] = Field(
        False,
        description='Flag to signal whether the order is intended for on-chain order placement. Only valid for non ECDSA-signed orders."\n',
    )
    timeout: Optional[int] = Field(
        None,
        description="User provided timeout in milliseconds. Can only be used to reduce the response time for quote requests if the default is too slow as values greater than the default will be capped to the default. Note that reducing the timeout can result in worse quotes because the reduced timeout might be too slow for some price estimators.\n",
    )


class OrderQuoteResponse(BaseModel):
    quote: OrderParameters
    from_: Optional[Address] = Field(None, alias="from")
    expiration: str = Field(
        ...,
        description="Expiration date of the offered fee. Order service might not accept\nthe fee after this expiration date. Encoded as ISO 8601 UTC.\n",
        examples=["1985-03-10T18:35:18.814523Z"],
    )
    id: Optional[int] = Field(
        None,
        description="Quote ID linked to a quote to enable providing more metadata when analysing order slippage.\n",
    )
    verified: bool = Field(
        ...,
        description="Whether it was possible to verify that the quoted amounts are accurate using a simulation.\n",
    )


class SolverCompetitionResponse(BaseModel):
    auctionId: Optional[int] = Field(
        None, description="The ID of the auction the competition info is for."
    )
    auctionStartBlock: Optional[int] = Field(
        None, description="Block that the auction started on."
    )
    transactionHashes: Optional[List[TransactionHash]] = Field(
        None,
        description="The hashes of the transactions for the winning solutions of this competition.\n",
    )
    referenceScores: Optional[Dict[str, BigUint]] = Field(
        None,
        description="The reference scores for each winning solver according to [CIP-67](https://forum.cow.fi/t/cip-67-moving-from-batch-auction-to-the-fair-combinatorial-auction/2967) (if available).\n",
    )
    auction: Optional[CompetitionAuction] = None
    solutions: Optional[List[SolverSettlement]] = Field(
        None,
        description="Maps from solver name to object describing that solver's settlement.",
    )


class OrderCreation(BaseModel):
    sellToken: Address = Field(..., description="see `OrderParameters::sellToken`")
    buyToken: Address = Field(..., description="see `OrderParameters::buyToken`")
    receiver: Optional[Address] = Field(
        None, description="see `OrderParameters::receiver`"
    )
    sellAmount: TokenAmount = Field(
        ..., description="see `OrderParameters::sellAmount`"
    )
    buyAmount: TokenAmount = Field(..., description="see `OrderParameters::buyAmount`")
    validTo: int = Field(..., description="see `OrderParameters::validTo`")
    feeAmount: TokenAmount = Field(..., description="see `OrderParameters::feeAmount`")
    kind: OrderKind = Field(..., description="see `OrderParameters::kind`")
    partiallyFillable: bool = Field(
        ..., description="see `OrderParameters::partiallyFillable`"
    )
    sellTokenBalance: Optional[SellTokenSource] = Field(
        "erc20", description="see `OrderParameters::sellTokenBalance`"
    )
    buyTokenBalance: Optional[BuyTokenDestination] = Field(
        "erc20", description="see `OrderParameters::buyTokenBalance`"
    )
    signingScheme: SigningScheme
    signature: Signature
    from_: Optional[Address] = Field(
        None,
        alias="from",
        description="If set, the backend enforces that this address matches what is decoded as the *signer* of the signature. This helps catch errors with invalid signature encodings as the backend might otherwise silently work with an unexpected address that for example does not have any balance.\n",
    )
    quoteId: Optional[int] = Field(
        None,
        description="Orders can optionally include a quote ID. This way the order can be linked to a quote and enable providing more metadata when analysing order slippage.\n",
    )
    appData: Union[AppData, AppDataHash] = Field(
        ...,
        description="This field comes in two forms for backward compatibility. The hash form will eventually stop being accepted.\n",
    )
    appDataHash: Optional[AppDataHash] = Field(
        None,
        description="May be set for debugging purposes. If set, this field is compared to what the backend internally calculates as the app data hash based on the contents of `appData`. If the hash does not match, an error is returned. If this field is set, then `appData` **MUST** be a string encoding of a JSON object.\n",
    )


class Order(OrderCreation, OrderMetaData):
    pass


class AuctionOrder(BaseModel):
    uid: UID
    sellToken: Address = Field(..., description="see `OrderParameters::sellToken`")
    buyToken: Address = Field(..., description="see `OrderParameters::buyToken`")
    sellAmount: TokenAmount = Field(
        ..., description="see `OrderParameters::sellAmount`"
    )
    buyAmount: TokenAmount = Field(..., description="see `OrderParameters::buyAmount`")
    created: str = Field(
        ...,
        description="Creation time of the order. Denominated in epoch seconds.",
        examples=["123456"],
    )
    validTo: int = Field(..., description="see `OrderParameters::validTo`")
    kind: OrderKind = Field(..., description="see `OrderParameters::kind`")
    receiver: Optional[Address] = Field(
        None, description="see `OrderParameters::receiver`"
    )
    owner: Address
    partiallyFillable: bool = Field(
        ..., description="see `OrderParameters::partiallyFillable`"
    )
    executed: TokenAmount = Field(
        ...,
        description="Currently executed amount of sell/buy token, depending on the order kind.\n",
    )
    preInteractions: List[InteractionData] = Field(
        ...,
        description="The pre-interactions that need to be executed before the first execution of the order.\n",
    )
    postInteractions: List[InteractionData] = Field(
        ...,
        description="The post-interactions that need to be executed after the execution of the order.\n",
    )
    sellTokenBalance: SellTokenSource = Field(
        ..., description="see `OrderParameters::sellTokenBalance`"
    )
    buyTokenBalance: BuyTokenDestination = Field(
        ..., description="see `OrderParameters::buyTokenBalance`"
    )
    class_: OrderClass = Field(..., alias="class")
    appData: AppDataHash
    signature: Signature
    protocolFees: List[FeePolicy] = Field(
        ...,
        description="The fee policies that are used to compute the protocol fees for this order.\n",
    )
    quote: Optional[Quote] = Field(None, description="A winning quote.\n")


class Auction(BaseModel):
    id: Optional[int] = Field(
        None,
        description="The unique identifier of the auction. Increment whenever the backend creates a new auction.\n",
    )
    block: Optional[int] = Field(
        None,
        description="The block number for the auction. Orders and prices are guaranteed to be valid on this block. Proposed settlements should be valid for this block as well.\n",
    )
    orders: Optional[List[AuctionOrder]] = Field(
        None, description="The solvable orders included in the auction.\n"
    )
    prices: Optional[AuctionPrices] = None
    surplusCapturingJitOrderOwners: Optional[List[Address]] = Field(
        None,
        description="List of addresses on whose surplus will count towards the objective value of their solution (unlike other orders that were created by the solver).\n",
    )
