import os
from typing import Iterable, Tuple, Type, TypeVar
import re
from typing import Any, Callable, Dict, List, Optional
from hexbytes import HexBytes
from web3 import Web3
from eth_abi.abi import encode, decode
from enum import Enum


from cow_py.common.chains import Chain
from cow_py.common.constants import (
    COMPOSABLE_COW_CONTRACT_CHAIN_ADDRESS_MAP,
    COW_PROTOCOL_SETTLEMENT_CONTRACT_CHAIN_ADDRESS_MAP,
)
from cow_py.composable.types import (
    ConditionalOrderParams,
    OwnerParams,
    PollResultError,
    PollResultSuccess,
)
from cow_py.composable.utils import decode_params, encode_params
from cow_py.codegen.__generated__.ComposableCow import (
    ComposableCow,
    IConditionalOrder_ConditionalOrderParams,
)

import abc
from typing import Generic
from eth_typing import HexStr, TypeStr

from cow_py.composable.types import (
    IsValidResult,
    PollParams,
    PollResult,
    ContextFactory,
    PollResultCode,
)
from cow_py.contracts.domain import domain
from cow_py.contracts.order import (
    Order,
    bytes32_to_balance_kind,
    bytes32_to_order_kind,
    compute_order_uid,
)
from cow_py.order_book.api import OrderBookApi
from cow_py.order_book.generated.model import UID

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


D = TypeVar("D")
S = TypeVar("S")


class ConditionalOrder(abc.ABC, Generic[D, S]):
    def __init__(
        self,
        handler: HexStr,
        data: D,
        salt: HexStr | None = None,
        has_off_chain_input: bool = False,
        chain: Chain = Chain.MAINNET,
    ):
        if salt is None:
            salt = Web3.to_hex(Web3.keccak(os.urandom(32)))
        if not Web3.is_address(handler):
            raise ValueError(f"Invalid handler: {handler}")
        if not is_valid_hex(salt) or len(Web3.to_bytes(hexstr=HexStr(salt))) != 32:
            raise ValueError(f"Invalid salt: {salt}")

        self.handler = handler
        self.salt = salt
        self.data = data
        self.static_input = self.transform_data_to_struct(data)
        self.has_off_chain_input = has_off_chain_input
        self.chain = chain

    @property
    def composableCow(self) -> ComposableCow:
        chain = self.chain
        return ComposableCow(
            chain, COMPOSABLE_COW_CONTRACT_CHAIN_ADDRESS_MAP[chain.chain_id].value
        )  # type: ignore

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

    @staticmethod
    def get_context_data(context: ContextFactory) -> HexStr | None:
        if context.factory_args == None:
            return HexStr("0x")

        return Web3.to_hex(
            encode(
                context.factory_args.args_type,
                context.factory_args.args,
            )
        )

    @property
    def create_calldata(self) -> HexStr:
        self.assert_is_valid()

        params_struct = {
            "handler": self.handler,
            "salt": self.salt,
            "static_input": self.static_input,
        }

        if self.context == None:
            return self.composableCow.build_calldata(
                "create",
                params_struct,
                True,
            )

        context_data = self.get_context_data(self.context)
        return self.composableCow.build_calldata(
            "create",
            params_struct,
            self.context.address,
            context_data,
            True,
        )

    @property
    def remove_calldata(self) -> str:
        self.assert_is_valid()
        return self.composableCow.build_calldata("remove", self.id)

    @property
    def id(self) -> HexStr:
        return Web3.to_hex(Web3.keccak(HexBytes(self.serialize())))

    @property
    def ctx(self) -> str:
        return self.id if self.is_single_order else "0x" + "0" * 64

    @property
    def leaf(self) -> ConditionalOrderParams:
        return ConditionalOrderParams(
            handler=self.handler,
            salt=self.salt,
            static_input=self.encode_static_input(),
        )

    @property
    def off_chain_input(self) -> HexStr:
        return HexStr("0x")

    @abc.abstractmethod
    def to_string(self, token_formatter: Optional[Callable] = None) -> str:
        pass

    @abc.abstractmethod
    def serialize(self) -> HexStr:
        pass

    @abc.abstractmethod
    def encode_static_input(self) -> HexStr:
        pass

    def encode_static_input_helper(
        self, order_data_types: Iterable[TypeStr], static_input: S
    ) -> HexStr:
        return Web3.to_hex(encode(order_data_types, [static_input]))

    async def poll(self, params: PollParams) -> PollResult:
        try:
            is_valid = self.is_valid()
            if not is_valid.is_valid:
                return PollResultError(
                    result=PollResultCode.DONT_TRY_AGAIN,
                    reason=f"InvalidConditionalOrder. Reason: {is_valid.reason}",
                )

            poll_result = await self.poll_validate(params)
            if poll_result:
                return poll_result

            is_authorized = await self.is_authorized(params)

            if not is_authorized:
                return PollResultError(
                    result=PollResultCode.DONT_TRY_AGAIN,
                    reason=f"NotAuthorized: Order {self.id} is not authorized for {params.owner} on chain {params.chain.chain_id}",
                )

            order, signature = await self.get_tradeable_order(params)

            print(order)

            order_uid = self.compute_order_uid(params.chain, params.owner, order)

            print(order_uid)

            is_order_in_orderbook = await self.is_order_in_orderbook(
                order_uid, params.order_book_api
            )

            if is_order_in_orderbook:
                poll_result = await self.handle_poll_failed_already_present(
                    order_uid, order, params
                )
                if poll_result:
                    return poll_result

                return PollResultError(
                    result=PollResultCode.TRY_NEXT_BLOCK,
                    reason="Order already in orderbook",
                )

            return PollResultSuccess(
                result=PollResultCode.SUCCESS,
                order=order,
                signature=signature,
            )

        except Exception as error:
            return PollResultError(
                result=PollResultCode.UNEXPECTED_ERROR,
                reason="Unexpected error",
                error=error,
            )

    async def is_authorized(self, params: OwnerParams) -> bool:
        return await self.composableCow.single_orders(params.owner, HexBytes(self.id))

    async def cabinet(self, params: OwnerParams) -> str:
        cabinet_bytes = await self.composableCow.cabinet(
            params.owner, HexBytes(self.ctx)
        )
        return cabinet_bytes.to_0x_hex()[2:]

    @abc.abstractmethod
    async def poll_validate(self, params: PollParams) -> Optional[PollResultError]:
        pass

    @abc.abstractmethod
    async def handle_poll_failed_already_present(
        self, order_uid: str, order: Order, params: PollParams
    ) -> Optional[PollResultError]:
        pass

    @abc.abstractmethod
    def transform_struct_to_data(self, params: S) -> D:
        pass

    @abc.abstractmethod
    def transform_data_to_struct(self, params: D) -> S:
        pass

    def assert_is_valid(self):
        is_valid_result = self.is_valid()
        if not is_valid_result.is_valid:
            raise ValueError(f"Invalid order: {is_valid_result.reason}")

    @staticmethod
    def leaf_to_id(leaf: ConditionalOrderParams) -> str:
        return Web3.to_hex(Web3.keccak(HexBytes(encode_params(leaf))))

    async def get_tradeable_order(self, params: PollParams) -> Tuple[Order, HexStr]:
        order, salt = await self.composableCow.get_tradeable_order_with_signature(
            params.owner,
            IConditionalOrder_ConditionalOrderParams(
                staticInput=HexBytes(self.leaf.static_input),
                handler=self.handler,
                salt=HexBytes(self.salt),
            ),
            HexBytes(self.off_chain_input),
            [],
        )
        return (
            Order(
                kind=bytes32_to_order_kind(order.kind),
                sell_amount=order.sellAmount,
                buy_amount=order.buyAmount,
                sell_token=order.sellToken,
                buy_token=order.buyToken,
                receiver=order.receiver,
                valid_to=order.validTo,
                app_data=order.appData.hex(),
                fee_amount=order.feeAmount,
                partially_fillable=order.partiallyFillable,
                sell_token_balance=bytes32_to_balance_kind(order.sellTokenBalance),
                buy_token_balance=bytes32_to_balance_kind(order.buyTokenBalance),
            ),
            Web3.to_hex(salt),
        )

    def compute_order_uid(self, chain: Chain, owner: str, order: Order) -> str:
        _domain = domain(
            chain,
            COW_PROTOCOL_SETTLEMENT_CONTRACT_CHAIN_ADDRESS_MAP[chain.chain_id].value,
        )
        return compute_order_uid(_domain, order, owner)

    async def is_order_in_orderbook(
        self, order_uid: str, order_book_api: OrderBookApi
    ) -> bool:
        try:
            await order_book_api.get_order_by_uid(UID(order_uid))
            return True
        except:
            return False

    @staticmethod
    def deserialize_helper(
        encoded_data: HexStr,
        handler: str,
        order_data_types: List[str],
        callback: Callable[[Any, HexStr], T],
    ) -> T:
        """
        A helper function for generically deserializing a conditional order.

        Args:
            encoded_data: The ABI-encoded IConditionalOrder.Params struct to deserialize.
            handler: Address of the handler for the conditional order.
            order_data_types: ABI types for the order's data struct.
            callback: A callback function that takes the deserialized data struct and the salt
                    and returns an instance of the class.

        Returns:
            An instance of the conditional order class.

        Raises:
            ValueError: If the handler doesn't match or if the encoded data is invalid.
        """
        try:
            decoded_params = decode_params(encoded_data)

            recovered_handler = Web3.to_checksum_address(decoded_params.handler)
            if recovered_handler.lower() != handler.lower():
                raise ValueError("HandlerMismatch")

            # Third, decode the data struct
            decoded_data = decode(
                order_data_types, Web3.to_bytes(hexstr=decoded_params.static_input)
            )[0]

            # Create a new instance of the class
            return callback(decoded_data, HexStr(decoded_params.salt))

        except ValueError as e:
            if str(e) == "HandlerMismatch":
                raise
            raise ValueError("InvalidSerializedConditionalOrder") from e


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
