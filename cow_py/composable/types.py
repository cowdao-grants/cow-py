from dataclasses import dataclass
from typing import ClassVar, List, Optional, Any, Union, Literal
from enum import Enum
from eth_typing import HexStr
from pymerkle import MerkleProof
from web3 import AsyncWeb3
from web3.types import BlockData

from cowdao_cowpy.common.chains import Chain
from cowdao_cowpy.contracts.order import Order
from cowdao_cowpy.order_book.api import OrderBookApi


@dataclass
class OwnerParams:
    owner: str
    chain: Chain
    provider: AsyncWeb3


@dataclass
class PollParams(OwnerParams):
    order_book_api: OrderBookApi
    proof: ClassVar[List[str]] = []
    block_info: Optional[BlockData] = None
    off_chain_input: str = "0x"


class ProofLocation(Enum):
    PRIVATE = 0
    EMITTED = 1
    SWARM = 2
    WAKU = 3
    RESERVED = 4
    IPFS = 5


@dataclass
class FactoryArgs:
    args: List[Any]
    args_type: List[str]


@dataclass
class ContextFactory:
    address: str
    factory_args: Optional[FactoryArgs] = None


@dataclass
class ConditionalOrderParams:
    handler: HexStr
    salt: HexStr
    static_input: HexStr


@dataclass
class ProofStruct:
    location: ProofLocation
    data: Union[str, HexStr]


@dataclass
class ProofWithParams:
    proof: MerkleProof
    params: ConditionalOrderParams


class PollResultCode(Enum):
    SUCCESS = "SUCCESS"
    UNEXPECTED_ERROR = "UNEXPECTED_ERROR"
    TRY_NEXT_BLOCK = "TRY_NEXT_BLOCK"
    TRY_ON_BLOCK = "TRY_ON_BLOCK"
    TRY_AT_EPOCH = "TRY_AT_EPOCH"
    DONT_TRY_AGAIN = "DONT_TRY_AGAIN"


@dataclass
class IsValidResult:
    is_valid: bool
    reason: Optional[str] = None


@dataclass
class PollResultSuccess:
    result: Literal[PollResultCode.SUCCESS]
    order: Order
    signature: str


@dataclass
class PollResultError:
    result: Literal[
        PollResultCode.UNEXPECTED_ERROR,
        PollResultCode.TRY_NEXT_BLOCK,
        PollResultCode.TRY_ON_BLOCK,
        PollResultCode.TRY_AT_EPOCH,
        PollResultCode.DONT_TRY_AGAIN,
    ]
    reason: str
    error: Optional[Exception] = None
    epoch: Optional[int] = None
    block_number: Optional[int] = None


PollResult = Union[PollResultSuccess, PollResultError]
