import os
from typing import Iterable, Tuple, Type, TypeVar
import re
from typing import Any, Callable, Dict, List, Optional
from hexbytes import HexBytes
from web3 import Web3
from eth_abi.abi import encode, decode
from enum import Enum


from cowdao_cowpy.common.chains import Chain
from cowdao_cowpy.common.constants import (
    COW_PROTOCOL_SETTLEMENT_CONTRACT_CHAIN_ADDRESS_MAP,
)
from cowdao_cowpy.composable.types import (
    ConditionalOrderParams,
    OwnerParams,
    PollResultError,
    PollResultSuccess,
)
from cowdao_cowpy.composable.utils import (
    convert_composable_cow_tradable_order_to_order_type,
    decode_params,
    encode_params,
    getComposableCoW,
)
from cowdao_cowpy.codegen.__generated__.ComposableCow import (
    ComposableCow,
    IConditionalOrder_ConditionalOrderParams,
)

import abc
from typing import Generic
from eth_typing import HexStr, TypeStr

from cowdao_cowpy.composable.types import (
    IsValidResult,
    PollParams,
    PollResult,
    ContextFactory,
    PollResultCode,
)
from cowdao_cowpy.contracts.domain import domain
from cowdao_cowpy.contracts.order import (
    Order,
    compute_order_uid,
)
from cowdao_cowpy.order_book.api import OrderBookApi
from cowdao_cowpy.order_book.generated.model import UID

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
    """
    An abstract base class from which all conditional orders should inherit.

    This class provides some basic functionality to help with handling conditional orders,
    such as:
    - Validating the conditional order
    - Creating a human-readable string representation of the conditional order
    - Serializing the conditional order for use with the `IConditionalOrder` struct
    - Getting any dependencies for the conditional order
    - Getting the off-chain input for the conditional order

    Note:
        Instances of conditional orders have an `id` property that is a `keccak256` hash of
        the serialized conditional order.

    Type Parameters:
        D: The type of the data structure used for friendly representation
        S: The type of the static input structure used by the contract
    """

    def __init__(
        self,
        handler: HexStr,
        data: D,
        salt: HexStr | None = None,
        has_off_chain_input: bool = False,
        chain: Chain = Chain.MAINNET,
    ):
        """
        A constructor that provides some basic validation for the conditional order.

        This constructor **MUST** be called by any class that inherits from `ConditionalOrder`.

        Note:
            The salt is optional and will be randomly generated if not provided.

        Args:
            handler: The address of the handler for the conditional order.
            data: The data of the order.
            salt: A 32-byte string used to salt the conditional order.
            has_off_chain_input: Whether the conditional order has off-chain input.
            chain: The blockchain chain to use.

        Raises:
            ValueError: If the handler is not a valid ethereum address.
            ValueError: If the salt is not a valid 32-byte string.
        """
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
        return getComposableCoW(self.chain)

    @property
    @abc.abstractmethod
    def is_single_order(self) -> bool:
        """
        Whether this conditional order represents a single order or multiple orders.
        """
        pass

    @property
    @abc.abstractmethod
    def order_type(self) -> str:
        """
        Get a descriptive name for the type of the conditional order (i.e twap, dca, etc).

        Returns:
            str: The concrete type of the conditional order.
        """
        pass

    @property
    def context(self) -> Optional[ContextFactory]:
        """
        Get the context dependency for the conditional order.

        This is used when calling `createWithContext` or `setRootWithContext` on a ComposableCoW-enabled Safe.

        Returns:
            Optional[ContextFactory]: The context dependency, if any.
        """
        return None

    @abc.abstractmethod
    def is_valid(self) -> IsValidResult:
        pass

    @property
    def create_calldata(self) -> HexStr:
        """
        Get the calldata for creating the conditional order.

        This will automatically determine whether to use `create` or `createWithContext` based on the
        order type's context dependency.

        Note:
            By default, this will cause the create to emit the `ConditionalOrderCreated` event.

        Returns:
            HexStr: The calldata for creating the conditional order.
        """
        self.assert_is_valid()

        params_struct = {
            "handler": self.handler,
            "salt": self.salt,
            "static_input": self.static_input,
        }

        if self.context is None:
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
    def id(self) -> HexStr:
        """
        Calculate the id of the conditional order (which also happens to be the key used for `ctx`
        in the ComposableCoW contract).

        This is a `keccak256` hash of the serialized conditional order.

        Returns:
            HexStr: The id of the conditional order.
        """
        return Web3.to_hex(Web3.keccak(HexBytes(self.serialize())))

    @property
    def ctx(self) -> str:
        """
        The context key of the order (bytes32(0) if a merkle tree is used, otherwise H(params))
        with which to lookup the cabinet.

        The context relates to the 'ctx' in the contract.
        """
        return self.id if self.is_single_order else "0x" + "0" * 64

    @property
    def leaf(self) -> ConditionalOrderParams:
        """
        Get the `leaf` of the conditional order. This is the data that is used to create the merkle tree.

        For the purposes of this library, the `leaf` is the `ConditionalOrderParams` struct.

        Returns:
            ConditionalOrderParams: The `leaf` of the conditional order.
        """
        return ConditionalOrderParams(
            handler=self.handler,
            salt=self.salt,
            static_input=self.encode_static_input(),
        )

    @property
    def off_chain_input(self) -> HexStr:
        """
        If the conditional order has off-chain input, return it!

        Note:
            This should be overridden by any conditional order that has off-chain input.

        Returns:
            HexStr: The off-chain input.
        """
        return HexStr("0x")

    async def poll(self, params: PollParams) -> PollResult:
        """
        Poll a conditional order to see if it is tradeable.

        Args:
            params: The polling parameters including owner, chain, provider, and orderbook API.

        Returns:
            PollResult: The poll result, which includes either the tradeable order and signature
                       or error information.

        Raises:
            Exception: If an unexpected error occurs during polling.
        """
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
            order_uid = self.compute_order_uid(params.chain, params.owner, order)
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

    @abc.abstractmethod
    async def poll_validate(self, params: PollParams) -> Optional[PollResultError]:
        """
        Allow concrete conditional orders to perform additional validation for the poll method.

        This will allow the concrete orders to decide when an order shouldn't be polled again.
        For example, if the order is expired. It also allows to signal when should the next check
        be done. For example, an order could signal that the validations will fail until a certain
        time or block.

        Args:
            params: The poll parameters.

        Returns:
            Optional[PollResultError]: None if the concrete order can't make a decision.
            Otherwise, it returns a PollResultError object.
        """
        pass

    @abc.abstractmethod
    async def handle_poll_failed_already_present(
        self, order_uid: str, order: Order, params: PollParams
    ) -> Optional[PollResultError]:
        """
        This method lets the concrete conditional order decide what to do if the order yielded
        in the polling is already present in the Orderbook API.

        The concrete conditional order will have a chance to schedule the next poll.
        For example, a TWAP order that has the current part already in the orderbook, can signal
        that the next poll should be done at the start time of the next part.

        Args:
            order_uid: The unique identifier of the order.
            order: The order data.
            params: The poll parameters.

        Returns:
            Optional[PollResultError]: The poll result if the concrete order makes a decision,
            None otherwise.
        """
        pass

    @abc.abstractmethod
    def transform_struct_to_data(self, params: S) -> D:
        """
        Convert the struct that the contract expects as an encoded `staticInput` into a friendly
        data object modelling the smart order.

        Note:
            This should be overridden by any conditional order that requires transformations.
            This implementation is a no-op if you use the same type for both.

        Args:
            params: Parameters in the contract's struct format.

        Returns:
            The data in the friendly format used by this class.
        """
        pass

    @abc.abstractmethod
    def transform_data_to_struct(self, params: D) -> S:
        """
        Converts a friendly data object modelling the smart order into the struct that the
        contract expects as an encoded `staticInput`.

        Note:
            This should be overridden by any conditional order that requires transformations.
            This implementation is a no-op if you use the same type for both.

        Args:
            params: Parameters in the friendly format used by this class.

        Returns:
            The data in the contract's struct format.
        """
        pass

    @staticmethod
    def get_context_data(context: ContextFactory) -> HexStr | None:
        """
        Get the encoded context data for a context factory.

        Args:
            context: The context factory containing the arguments to encode.

        Returns:
            HexStr | None: The encoded context data, or None if no factory args are present.
        """
        if context.factory_args is None:
            return HexStr("0x")

        return Web3.to_hex(
            encode(
                context.factory_args.args_type,
                context.factory_args.args,
            )
        )

    @property
    def remove_calldata(self) -> str:
        """
        Get the calldata for removing a conditional order that was created as a single order.

        Returns:
            str: The calldata for removing the conditional order.

        Raises:
            ValueError: If the order is not valid.
        """
        self.assert_is_valid()
        return self.composableCow.build_calldata("remove", self.id)

    async def is_authorized(self, params: OwnerParams) -> bool:
        """
        Checks if the owner authorized the conditional order.

        Args:
            params: owner context, to be able to check if the order is authorized

        Returns:
            bool: True if the owner authorized the order, false otherwise.
        """
        return await self.composableCow.single_orders(params.owner, HexBytes(self.id))

    async def cabinet(self, params: OwnerParams) -> str:
        """
        Checks the value in the cabinet for a given owner and chain.

        Args:
            params: owner context, to be able to check the cabinet

        Returns:
            str: The cabinet value as a hex string without the '0x' prefix.
        """
        cabinet_bytes = await self.composableCow.cabinet(
            params.owner, HexBytes(self.ctx)
        )
        return Web3.to_hex(cabinet_bytes)[2:]

    @abc.abstractmethod
    def to_string(self, token_formatter: Optional[Callable] = None) -> str:
        """
        Create a human-readable string representation of the conditional order.

        Args:
            token_formatter: An optional function that takes an address and an amount and returns a human-readable string.

        Returns:
            str: A human-readable representation of the conditional order.
        """
        pass

    @abc.abstractmethod
    def serialize(self) -> HexStr:
        """
        Serializes the conditional order into its ABI-encoded form.

        Returns:
            HexStr: The equivalent of `IConditionalOrder.Params` for the conditional order.
        """
        pass

    @abc.abstractmethod
    def encode_static_input(self) -> HexStr:
        """
        Encode the `staticInput` for the conditional order.

        Returns:
            HexStr: The ABI-encoded `staticInput` for the conditional order.
        """
        pass

    def encode_static_input_helper(
        self, order_data_types: Iterable[TypeStr], static_input: S
    ) -> HexStr:
        """
        A helper function for generically serializing a conditional order's static input.

        Args:
            order_data_types: ABI types for the order's data struct.
            static_input: The order's data struct.

        Returns:
            HexStr: An ABI-encoded representation of the order's data struct.
        """
        return Web3.to_hex(encode(order_data_types, [static_input]))

    def assert_is_valid(self):
        """
        Assert that the conditional order is valid.

        Raises:
            ValueError: If the order is not valid, with the reason included in the error message.
        """
        is_valid_result = self.is_valid()
        if not is_valid_result.is_valid:
            raise ValueError(f"Invalid order: {is_valid_result.reason}")

    @staticmethod
    def leaf_to_id(leaf: ConditionalOrderParams) -> str:
        """
        Calculate the id of the conditional order.

        Args:
            leaf: The `leaf` representing the conditional order.

        Returns:
            str: The id of the conditional order.
        """
        return Web3.to_hex(Web3.keccak(HexBytes(encode_params(leaf))))

    async def get_tradeable_order(self, params: PollParams) -> Tuple[Order, HexStr]:
        """
        Get the tradeable order and signature from the ComposableCow contract.

        Args:
            params: The poll parameters including owner information.

        Returns:
            Tuple[Order, HexStr]: A tuple containing the order data and its signature.
        """
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
            convert_composable_cow_tradable_order_to_order_type(order),
            Web3.to_hex(salt),
        )

    def compute_order_uid(self, chain: Chain, owner: str, order: Order) -> str:
        """
        Compute the unique identifier for an order.

        Args:
            chain: The blockchain chain.
            owner: The order owner's address.
            order: The order data.

        Returns:
            str: The unique identifier for the order.
        """
        _domain = domain(
            chain,
            COW_PROTOCOL_SETTLEMENT_CONTRACT_CHAIN_ADDRESS_MAP[chain.chain_id].value,
        )
        return compute_order_uid(_domain, order, owner)

    async def is_order_in_orderbook(
        self, order_uid: str, order_book_api: OrderBookApi
    ) -> bool:
        """
        Check if an order exists in the orderbook.

        Args:
            order_uid: The unique identifier of the order.
            order_book_api: The orderbook API instance.

        Returns:
            bool: True if the order exists in the orderbook, False otherwise.
        """
        try:
            await order_book_api.get_order_by_uid(UID(order_uid))
            return True

        except:  # noqa: E722
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
            T: An instance of the conditional order class.

        Raises:
            ValueError: If the handler doesn't match ("HandlerMismatch") or if the encoded data
                       is invalid ("InvalidSerializedConditionalOrder").
        """
        decoded_params = decode_params(encoded_data)

        recovered_handler = Web3.to_checksum_address(decoded_params.handler)
        if recovered_handler.lower() != handler.lower():
            raise ValueError("HandlerMismatch")

        decoded_data = decode(
            order_data_types, Web3.to_bytes(hexstr=decoded_params.static_input)
        )[0]

        return callback(decoded_data, HexStr(decoded_params.salt))


class ConditionalOrderFactory:
    """
    A factory class for creating conditional orders.

    This class maintains a registry of order types and their corresponding classes,
    allowing for dynamic creation of conditional orders based on their type.
    """

    registry: Dict[str, Type[ConditionalOrder]] = {}

    @classmethod
    def register(cls, order_type: str, order_class: Type[ConditionalOrder]):
        """
        Register a new conditional order type.

        Args:
            order_type: The identifier for this type of conditional order.
            order_class: The class that implements this type of conditional order.
        """
        cls.registry[order_type] = order_class

    @classmethod
    def create(cls, order_type: str, params: Dict[str, Any]) -> ConditionalOrder:
        """
        Create a new conditional order of the specified type.

        Args:
            order_type: The type of conditional order to create.
            params: The parameters to pass to the order's constructor.

        Returns:
            ConditionalOrder: A new instance of the specified conditional order type.

        Raises:
            ValueError: If the specified order type is not registered.
        """
        if order_type not in cls.registry:
            raise ValueError(f"Unknown order type: {order_type}")
        return cls.registry[order_type](**params)
