from dataclasses import dataclass
from enum import Enum
from typing import Literal, Optional, Union

from eth_account.messages import _hash_eip191_message, encode_typed_data
from eth_typing import Hash32, HexStr
from eth_utils.conversions import to_bytes, to_hex


@dataclass
class Order:
    # Sell token address.
    sellToken: str
    # Buy token address.
    buyToken: str
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
    sellAmount: int
    # The order buy amount.
    #
    # For fill or kill sell orders, this amount represents the minimum buy amount
    # that can be executed in the trade. For fill or kill buy orders, this amount
    # represents the exact buy amount that will be executed. For partial fill
    # orders, this represents a component of the limit price fraction.
    #
    buyAmount: int
    # The timestamp this order is valid until
    validTo: int
    # Arbitrary application specific data that can be added to an order. This can
    # also be used to ensure uniqueness between two orders with otherwise the
    # exact same parameters.
    appData: str
    # Fee to give to the protocol.
    feeAmount: int
    # The order kind.
    kind: str
    # Specifies whether or not the order is partially fillable.
    partiallyFillable: bool = False
    # Specifies how the sell token balance will be withdrawn. It can either be
    # taken using ERC20 token allowances made directly to the Vault relayer
    # (default) or using Balancer Vault internal or external balances.
    sellTokenBalance: Optional[str] = None
    # Specifies how the buy token balance will be paid. It can either be paid
    # directly in ERC20 tokens (default) in Balancer Vault internal balances.
    buyTokenBalance: Optional[str] = None


# Gnosis Protocol v2 order cancellation data.
@dataclass
class OrderCancellations:
    orderUids: bytearray


# Marker address to indicate that an order is buying Ether.
#
# Note that this address is only has special meaning in the `buyToken` and will
# be treated as a ERC20 token address in the `sellToken` position, causing the
# settlement to revert.
BUY_ETH_ADDRESS = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"

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


# /**
#  * The EIP-712 type fields definition for a Gnosis Protocol v2 order.
#  */
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
# The EIP-712 type fields definition for a Gnosis Protocol v2 order.
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
    elif balance == OrderBalance.INTERNAL:
        return OrderBalance.INTERNAL.value
    else:
        raise ValueError(f"Invalid order balance {balance}")


ZERO_ADDRESS = "0x" + "00" * 20


def normalize_order(order: Order):
    if order.receiver == ZERO_ADDRESS:
        raise ValueError("receiver cannot be address(0)")

    return {
        "sellToken": order.sellToken,
        "buyToken": order.buyToken,
        "receiver": order.receiver if order.receiver else ZERO_ADDRESS,
        "sellAmount": order.sellAmount,
        "buyAmount": order.buyAmount,
        "validTo": order.validTo,
        "appData": hashify(order.appData),
        "feeAmount": order.feeAmount,
        "kind": order.kind,
        "partiallyFillable": order.partiallyFillable,
        "sellTokenBalance": (
            order.sellTokenBalance
            if order.sellTokenBalance
            else OrderBalance.ERC20.value
        ),
        "buyTokenBalance": normalize_buy_token_balance(order.buyTokenBalance),
    }


def hash_typed_data(domain, types, data) -> Hash32:
    """
    Compute the 32-byte signing hash for the specified order.

    :param domain: The EIP-712 domain separator to compute the hash for.
    :param types: The typed data types.
    :param data: The data to compute the digest for.
    :return: Hex-encoded 32-byte order digest.
    """
    encoded_data = encode_typed_data(
        domain_data=domain, message_types=types, message_data=data
    )
    return _hash_eip191_message(encoded_data)


def hash_order(domain, order):
    """
    Compute the 32-byte signing hash for the specified order.

    :param domain: The EIP-712 domain separator to compute the hash for.
    :param order: The order to compute the digest for.
    :return: Hex-encoded 32-byte order digest.
    """
    return hash_typed_data(domain, ORDER_TYPE_FIELDS, normalize_order(order))


def hash_order_cancellation(domain, order_uid) -> str:
    """
    Compute the 32-byte signing hash for the specified cancellation.

    :param domain: The EIP-712 domain separator to compute the hash for.
    :param order_uid: The unique identifier of the order to cancel.
    :return: Hex-encoded 32-byte order digest.
    """
    return hash_order_cancellations(domain, [order_uid])


def hash_order_cancellations(domain_data, order_uids) -> str:
    """
    Compute the 32-byte signing hash for the specified order cancellations.

    :param domain_data: The EIP-712 domain separator to compute the hash for.
    :param order_uids: The unique identifiers of the orders to cancel.
    :return: Hex-encoded 32-byte order digest.
    """
    return _hash_eip191_message(
        encode_typed_data(
            domain_data,
            message_types={"OrderCancellations": CANCELLATIONS_TYPE_FIELDS},
            message_data={"orderUids": order_uids},
        )
    ).hex()


# The byte length of an order UID.
ORDER_UID_LENGTH = 56


@dataclass
class OrderUidParams:
    # The EIP-712 order struct hash.
    orderDigest: str
    # The owner of the order.
    owner: str
    # The timestamp this order is valid until.
    validTo: int
