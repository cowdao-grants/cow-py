from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Literal, Optional, Union

from eth_account.messages import _hash_eip191_message, encode_typed_data
from eth_typing import Hash32, HexStr
from eth_abi.packed import encode_packed

from eth_utils.conversions import to_bytes, to_hex
from hexbytes import HexBytes
from web3.constants import ADDRESS_ZERO
from web3 import Web3

from cowdao_cowpy.contracts.domain import TypedDataDomain

# The byte length of an order UID.
ORDER_UID_LENGTH = 56


@dataclass
class Order:
    # Sell token address.
    sell_token: str = field(metadata={"alias": "sellToken"})
    # Buy token address.
    buy_token: str = field(metadata={"alias": "buyToken"})
    # An optional address to receive the proceeds of the trade instead of the
    # owner (i.e. the order signer).
    receiver: str
    # The order sell amount.
    #
    # For fill or kill sell orders, this amount represents the exact sell amount
    # that will be executed in the trade. For fill or kill buy orders, this
    # amount represents the maximum sell amount that can be executed. For partial
    # fill orders, this represents a component of the limit price fraction.
    #
    sell_amount: str = field(metadata={"alias": "sellAmount"})
    # The order buy amount.
    #
    # For fill or kill sell orders, this amount represents the minimum buy amount
    # that can be executed in the trade. For fill or kill buy orders, this amount
    # represents the exact buy amount that will be executed. For partial fill
    # orders, this represents a component of the limit price fraction.
    #
    buy_amount: str = field(metadata={"alias": "buyAmount"})
    # The timestamp this order is valid until
    valid_to: int = field(metadata={"alias": "validTo"})
    # Arbitrary application specific data that can be added to an order. This can
    # also be used to ensure uniqueness between two orders with otherwise the
    # exact same parameters.
    app_data: str = field(metadata={"alias": "appData"})
    # Fee to give to the protocol.
    fee_amount: str = field(metadata={"alias": "feeAmount"})
    # The order kind.
    kind: str
    # Specifies whether or not the order is partially fillable.
    partially_fillable: bool = field(
        default=False, metadata={"alias": "partiallyFillable"}
    )
    # Specifies how the sell token balance will be withdrawn. It can either be
    # taken using ERC20 token allowances made directly to the Vault relayer
    # (default) or using Balancer Vault internal or external balances.
    sell_token_balance: Optional[str] = field(
        default=None, metadata={"alias": "sellTokenBalance"}
    )
    # Specifies how the buy token balance will be paid. It can either be paid
    # directly in ERC20 tokens (default) in Balancer Vault internal balances.
    buy_token_balance: Optional[str] = field(
        default=None, metadata={"alias": "buyTokenBalance"}
    )

    def __getattr__(self, name):
        for f in self.__dataclass_fields__.values():
            if f.metadata.get("alias") == name:
                return getattr(self, f.name)
        raise AttributeError(
            f"'{type(self).__name__}' object has no attribute '{name}'"
        )

    def __setattr__(self, name, value):
        for f in self.__dataclass_fields__.values():
            if f.metadata.get("alias") == name:
                return super().__setattr__(f.name, value)
        return super().__setattr__(name, value)


# Gnosis Protocol v2 order cancellation data.
@dataclass
class OrderCancellations:
    order_uids: bytearray


BytesLike = Union[str, bytes, HexStr]

HashLike = Union[BytesLike, int]


class OrderKind(Enum):
    SELL = "sell"
    BUY = "buy"


class OrderBalance(Enum):
    # Use ERC20 token balances.
    ERC20 = "erc20"
    # Use Balancer Vault external balances.

    # This can only be specified specified for the sell balance and allows orders
    # to re-use Vault ERC20 allowances. When specified for the buy balance, it
    # will be treated as {@link OrderBalance.ERC20}.
    EXTERNAL = "external"
    # Use Balancer Vault internal balances.
    INTERNAL = "internal"


@dataclass
class OrderUidParams:
    # The EIP-712 order struct hash.
    order_digest: str = field(metadata={"alias": "orderDigest"})
    # The owner of the order.
    owner: str
    # The timestamp this order is valid until.
    validTo: int


# /**
#  * The EIP-712 type fields definition for a Gnosis Protocol v2 order.
#  */
# The EIP-712 type fields definition for a Gnosis Protocol v2 order.
ORDER_TYPE_FIELDS = [
    dict(name="sellToken", type="address"),
    dict(name="buyToken", type="address"),
    dict(name="receiver", type="address"),
    dict(name="sellAmount", type="uint256"),
    dict(name="buyAmount", type="uint256"),
    dict(name="validTo", type="uint32"),
    dict(name="appData", type="bytes32"),
    dict(name="feeAmount", type="uint256"),
    dict(name="kind", type="string"),
    dict(name="partiallyFillable", type="bool"),
    dict(name="sellTokenBalance", type="string"),
    dict(name="buyTokenBalance", type="string"),
]
CANCELLATIONS_TYPE_FIELDS = [
    dict(name="orderUids", type="bytes[]"),
]


def hashify(h: Union[int, str, bytes]) -> str:
    """
    Normalizes an app data value to a 32-byte hash.
    :param h: A hash-like value to normalize. Can be an integer, hexadecimal string, or bytes.
    :return: A 32-byte hash encoded as a hex-string.
    """
    if isinstance(h, int):
        # Convert the integer to a hexadecimal string and pad it to 64 characters
        return f"0x{h:064x}"
    elif isinstance(h, str):
        # Convert string to bytes, then pad it to 32 bytes (64 hex characters)
        return to_hex(to_bytes(hexstr=h).rjust(32, b"\0"))
    elif isinstance(h, bytes):
        # Pad the bytes to 32 bytes (64 hex characters)
        return to_hex(h.rjust(32, b"\0"))
    else:
        raise ValueError("Input must be an integer, a hexadecimal string, or bytes.")


def normalize_buy_token_balance(
    balance: Optional[str],
) -> Literal["erc20", "internal"]:
    """
    Normalizes the balance configuration for a buy token.

    :param balance: The balance configuration.
    :return: The normalized balance configuration.
    """
    if balance in [None, OrderBalance.ERC20.value, OrderBalance.EXTERNAL.value]:
        return OrderBalance.ERC20.value
    elif balance == OrderBalance.INTERNAL.value:
        return OrderBalance.INTERNAL.value
    else:
        raise ValueError(f"Invalid order balance {balance}")


def normalize_order(order: Order) -> Dict[str, Union[str, int]]:
    if order.receiver == ADDRESS_ZERO:
        raise ValueError("receiver cannot be address(0)")

    return {
        "sellToken": order.sell_token,
        "buyToken": order.buy_token,
        "receiver": order.receiver if order.receiver else ADDRESS_ZERO,
        "sellAmount": order.sell_amount,
        "buyAmount": order.buy_amount,
        "validTo": order.valid_to,
        "appData": hashify(order.app_data),
        "feeAmount": order.fee_amount,
        "kind": order.kind,
        "partiallyFillable": order.partially_fillable,
        "sellTokenBalance": (
            order.sell_token_balance
            if order.sell_token_balance
            else OrderBalance.ERC20.value
        ),
        "buyTokenBalance": normalize_buy_token_balance(order.buy_token_balance),
    }


def hash_typed_data(
    domain: TypedDataDomain, types: Dict[str, Any], data: Dict[str, Any]
) -> Hash32:
    """
    Compute the 32-byte signing hash for the specified order.

    :param domain: The EIP-712 domain separator to compute the hash for.
    :param types: The typed data types.
    :param data: The data to compute the digest for.
    :return: Hex-encoded 32-byte order digest.
    """
    encoded_data = encode_typed_data(
        domain_data=domain.to_dict(), message_types=types, message_data=data
    )
    return _hash_eip191_message(encoded_data)


def hash_order(domain: TypedDataDomain, order: Order) -> Hash32:
    """
    Compute the 32-byte signing hash for the specified order.

    :param domain: The EIP-712 domain separator to compute the hash for.
    :param order: The order to compute the digest for.
    :return: Hex-encoded 32-byte order digest.
    """
    return hash_typed_data(domain, {"Order": ORDER_TYPE_FIELDS}, normalize_order(order))


def hash_order_cancellation(domain: TypedDataDomain, order_uid: str) -> str:
    """
    Compute the 32-byte signing hash for the specified cancellation.

    :param domain: The EIP-712 domain separator to compute the hash for.
    :param order_uid: The unique identifier of the order to cancel.
    :return: Hex-encoded 32-byte order digest.
    """
    return hash_order_cancellations(domain, [order_uid])


def hash_order_cancellations(
    domain_data: TypedDataDomain, order_uids: list[str]
) -> str:
    """
    Compute the 32-byte signing hash for the specified order cancellations.

    :param domain_data: The EIP-712 domain separator to compute the hash for.
    :param order_uids: The unique identifiers of the orders to cancel.
    :return: Hex-encoded 32-byte order digest.
    """
    return _hash_eip191_message(
        encode_typed_data(
            domain_data.to_dict(),
            message_types={"OrderCancellations": CANCELLATIONS_TYPE_FIELDS},
            message_data={"orderUids": order_uids},
        )
    ).hex()


def pack_order_uid_params(params: OrderUidParams) -> str:
    """
    Compute the unique identifier describing a user order in the settlement contract.

    Args:
        params (OrderUidParams): The parameters used for computing the order's unique identifier.
            - order_digest: bytes32 hash of the order
            - owner: Ethereum address of the order owner
            - validTo: Order validity timestamp

    Returns:
        str: A hex string that unequivocally identifies the order of the user.
    """
    # Convert valid_to to uint32
    valid_to_uint32 = params.validTo & 0xFFFFFFFF

    # Pack the parameters using eth_abi.encode_packed
    packed = encode_packed(
        ["bytes32", "address", "uint32"],
        [
            Web3.to_bytes(hexstr=HexStr(params.order_digest)),
            Web3.to_checksum_address(params.owner),
            valid_to_uint32,
        ],
    )

    return Web3.to_hex(packed)


def compute_order_uid(domain: TypedDataDomain, order: Order, owner: str) -> str:
    order_hash = hash_order(domain, order)
    # Computes the order UID for an order and the given owner.
    return pack_order_uid_params(
        OrderUidParams(
            order_digest=Web3.to_hex(order_hash),
            owner=owner,
            validTo=order.valid_to,
        )
    )


def bytes32_to_order_kind(kind_bytes: HexBytes) -> str:
    KIND_SELL = HexBytes(
        "0xf3b277728b3fee749481eb3e0b3b48980dbbab78658fc419025cb16eee346775"
    )
    KIND_BUY = HexBytes(
        "0x6ed88e868af0a1983e3886d5f3e95a2fafbd6c3450bc229e27342283dc429ccc"
    )

    if kind_bytes == KIND_SELL:
        return "sell"
    elif kind_bytes == KIND_BUY:
        return "buy"
    raise ValueError(f"Invalid order kind: {kind_bytes.hex()}")


def bytes32_to_balance_kind(balance_bytes: HexBytes) -> str:
    BALANCE_ERC20 = HexBytes(
        "0x5a28e9363bb942b639270062aa6bb295f434bcdfc42c97267bf003f272060dc9"
    )
    BALANCE_EXTERNAL = HexBytes(
        "0xabee3b73373acd583a130924aad6dc38cfdc44ba0555ba94ce2ff63980ea0632"
    )
    BALANCE_INTERNAL = HexBytes(
        "0x4ac99ace14ee0a5ef932dc609df0943ab7ac16b7583634612f8dc35a4289a6ce"
    )

    if balance_bytes == BALANCE_ERC20:
        return "erc20"
    elif balance_bytes == BALANCE_EXTERNAL:
        return "external"
    elif balance_bytes == BALANCE_INTERNAL:
        return "internal"
    raise ValueError(f"Invalid balance kind: {balance_bytes.hex()}")
