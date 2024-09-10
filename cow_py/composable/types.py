from typing import TypedDict, Literal, Union, Dict, Any
from enum import Enum
from typing import List, Optional
from eth_typing import HexStr


class PollParams(TypedDict):
    owner: str
    chainId: int
    provider: Any
    orderBookApi: Any
    offchainInput: str
    proof: List[str]
    blockInfo: Dict[str, int]


class GPv2OrderStruct(TypedDict):
    sellToken: str
    buyToken: str
    receiver: str
    sellAmount: int
    buyAmount: int
    validTo: int
    appData: str
    feeAmount: int
    kind: str
    partiallyFillable: bool
    sellTokenBalance: str
    buyTokenBalance: str


class ProofLocation(Enum):
    PRIVATE = 0
    EMITTED = 1
    SWARM = 2
    WAKU = 3
    RESERVED = 4
    IPFS = 5


class ContextFactory(TypedDict):
    address: str
    factory_args: Optional[dict]


class ConditionalOrderParams(TypedDict):
    handler: str
    salt: HexStr
    static_input: HexStr


class ProofStruct(TypedDict):
    location: ProofLocation
    data: Union[str, HexStr]


class ProofWithParams(TypedDict):
    proof: List[str]
    params: ConditionalOrderParams


class PollResultCode(Enum):
    SUCCESS = "SUCCESS"
    UNEXPECTED_ERROR = "UNEXPECTED_ERROR"
    TRY_NEXT_BLOCK = "TRY_NEXT_BLOCK"
    TRY_ON_BLOCK = "TRY_ON_BLOCK"
    TRY_AT_EPOCH = "TRY_AT_EPOCH"
    DONT_TRY_AGAIN = "DONT_TRY_AGAIN"


class IsValidResult(TypedDict):
    is_valid: bool
    reason: Optional[str]


OrderKind = Literal["sell", "buy"]
OrderBalance = Literal["erc20", "external", "internal"]


class PollResultSuccess(TypedDict):
    result: Literal[PollResultCode.SUCCESS]
    order: Dict[str, Any]
    signature: str


class PollResultError(TypedDict):
    result: Literal[
        PollResultCode.UNEXPECTED_ERROR,
        PollResultCode.TRY_NEXT_BLOCK,
        PollResultCode.TRY_ON_BLOCK,
        PollResultCode.TRY_AT_EPOCH,
        PollResultCode.DONT_TRY_AGAIN,
    ]
    reason: str
    error: Optional[Exception]
    epoch: Optional[int]
    blockNumber: Optional[int]


PollResult = Union[PollResultSuccess, PollResultError]
