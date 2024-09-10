from typing import Tuple, Type, TypeVar
import re
from typing import Any, Callable, Dict, List, Optional
from web3 import Web3
from enum import Enum

from cow_py.composable.types import ConditionalOrderParams
from cow_py.composable.utils import encode_params

import abc
from typing import Generic
from eth_typing import HexStr

from cow_py.composable.types import (
    IsValidResult,
    PollParams,
    PollResult,
    ContextFactory,
    GPv2OrderStruct,
    PollResultCode,
)

T = TypeVar("T", bound="ConditionalOrder")


class OrderKind(Enum):
    SELL = "sell"
    BUY = "buy"


class OrderBalance(Enum):
    ERC20 = "erc20"
    EXTERNAL = "external"
    INTERNAL = "internal"


def is_valid_hex(value: str) -> bool:
    return bool(re.match(r"^0x[a-fA-F0-9]+$", value))


T = TypeVar("T")
S = TypeVar("S")


class ConditionalOrder(abc.ABC, Generic[T, S]):
    def __init__(
        self, handler: str, salt: HexStr, data: T, has_off_chain_input: bool = False
    ):
        if not Web3.isAddress(handler):
            raise ValueError(f"Invalid handler: {handler}")
        if not Web3.isHex(salt) or len(Web3.toBytes(hexstr=salt)) != 32:
            raise ValueError(f"Invalid salt: {salt}")

        self.handler = handler
        self.salt = salt
        self.data = data
        self.static_input = self.transform_data_to_struct(data)
        self.has_off_chain_input = has_off_chain_input

    @property
    @abc.abstractmethod
    def is_single_order(self) -> bool:
        pass

    @property
    @abc.abstractmethod
    def order_type(self) -> str:
        pass

    @property
    def context(self) -> Optional[ContextFactory]:
        return None

    @abc.abstractmethod
    def is_valid(self) -> IsValidResult:
        pass

    @property
    def create_calldata(self) -> str:
        self.assert_is_valid()
        # Implement create_calldata logic here
        return "0x"  # Placeholder

    @property
    def remove_calldata(self) -> str:
        self.assert_is_valid()
        # Implement remove_calldata logic here
        return "0x"  # Placeholder

    @property
    def id(self) -> str:
        return Web3.keccak(text=self.serialize()).hex()

    @property
    def ctx(self) -> str:
        return self.id if self.is_single_order else "0x" + "0" * 64

    @property
    def off_chain_input(self) -> str:
        return "0x"

    @abc.abstractmethod
    def to_string(self, token_formatter: Optional[Callable] = None) -> str:
        pass

    @abc.abstractmethod
    def serialize(self) -> str:
        pass

    @abc.abstractmethod
    def encode_static_input(self) -> str:
        pass

    async def poll(self, params: PollParams) -> PollResult:
        try:
            is_valid = self.is_valid()
            if not is_valid["is_valid"]:
                return {
                    "result": PollResultCode.DONT_TRY_AGAIN,
                    "reason": f"InvalidConditionalOrder. Reason: {is_valid['reason']}",
                }

            poll_result = await self.poll_validate(params)
            if poll_result:
                return poll_result

            is_authorized = await self.is_authorized(params)
            if not is_authorized:
                return {
                    "result": PollResultCode.DONT_TRY_AGAIN,
                    "reason": f"NotAuthorized: Order {self.id} is not authorized for {params['owner']} on chain {params['chain_id']}",
                }

            # Implement logic to get tradeable order and signature
            order, signature = await self.get_tradeable_order(params)

            # Check if the order is already in the order book
            order_uid = await self.compute_order_uid(
                params["chain_id"], params["owner"], order
            )
            is_order_in_orderbook = await self.is_order_in_orderbook(
                order_uid, params["order_book_api"]
            )

            if is_order_in_orderbook:
                poll_result = await self.handle_poll_failed_already_present(
                    order_uid, order, params
                )
                if poll_result:
                    return poll_result

                return {
                    "result": PollResultCode.TRY_NEXT_BLOCK,
                    "reason": "Order already in orderbook",
                }

            return {
                "result": PollResultCode.SUCCESS,
                "order": order,
                "signature": signature,
            }

        except Exception as error:
            return {
                "result": PollResultCode.UNEXPECTED_ERROR,
                "error": str(error),
            }

    async def is_authorized(self, params: Dict[str, Any]) -> bool:
        # Implement is_authorized logic here
        return True  # Placeholder

    async def cabinet(self, params: Dict[str, Any]) -> str:
        # Implement cabinet logic here
        return "0x"  # Placeholder

    @abc.abstractmethod
    async def poll_validate(self, params: PollParams) -> Optional[Dict[str, Any]]:
        pass

    @abc.abstractmethod
    async def handle_poll_failed_already_present(
        self, order_uid: str, order: GPv2OrderStruct, params: PollParams
    ) -> Optional[Dict[str, Any]]:
        pass

    @abc.abstractmethod
    def transform_struct_to_data(self, params: S) -> T:
        pass

    @abc.abstractmethod
    def transform_data_to_struct(self, params: T) -> S:
        pass

    @classmethod
    def deserialize_helper(
        cls, s: str, handler: str, order_data_types: List[str], callback: Callable
    ):
        # Implement deserialize_helper logic here
        pass

    def assert_is_valid(self):
        is_valid_result = self.is_valid()
        if not is_valid_result["is_valid"]:
            raise ValueError(f"Invalid order: {is_valid_result['reason']}")

    @staticmethod
    def leaf_to_id(leaf: ConditionalOrderParams) -> str:
        return Web3.keccak(text=encode_params(leaf)).hex()

    async def get_tradeable_order(
        self, params: PollParams
    ) -> Tuple[GPv2OrderStruct, str]:
        # Implement get_tradeable_order logic here
        pass

    async def compute_order_uid(
        self, chain_id: int, owner: str, order: GPv2OrderStruct
    ) -> str:
        # Implement compute_order_uid logic here
        pass

    async def is_order_in_orderbook(self, order_uid: str, order_book_api: Any) -> bool:
        # Implement is_order_in_orderbook logic here
        pass


class ConditionalOrderFactory:
    registry: Dict[str, Type[ConditionalOrder]] = {}

    @classmethod
    def register(cls, order_type: str, order_class: Type[ConditionalOrder]):
        cls.registry[order_type] = order_class

    @classmethod
    def create(cls, order_type: str, params: Dict[str, Any]) -> ConditionalOrder:
        if order_type not in cls.registry:
            raise ValueError(f"Unknown order type: {order_type}")
        return cls.registry[order_type](**params)
