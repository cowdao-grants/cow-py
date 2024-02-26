from eth_account.messages import SignableMessage, encode_typed_data
from dataclasses import dataclass
from enum import Enum
from typing import Literal, Optional, Union
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


# import { BigNumberish, BytesLike, ethers } from "ethers";

# import { TypedDataDomain, TypedDataTypes } from "./types/ethers";


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

# /**
#  * Gnosis Protocol v2 order flags.
#  */
# export type OrderFlags = Pick<
#   Order,
#   "kind" | "partiallyFillable" | "sellTokenBalance" | "buyTokenBalance"
# >;


# /**
#  * A timestamp value.
#  */
# export type Timestamp = number | Date;

# /**
#  * A hash-like app data value.
#  */
# export type HashLike = BytesLike | number;


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

#  The EIP-712 type hash for a Gnosis Protocol v2 order.

# ORDER_TYPE_HASH =
# export const ORDER_TYPE_HASH = ethers.utils.id(
#   `Order(${ORDER_TYPE_FIELDS.map(({ name, type }) => `${type} ${name}`).join(
#     ",",
#   )})`,
# );


# export function timestamp(t: Timestamp): number {
#   return typeof t === "number" ? t : ~~(t.getTime() / 1000);
# }
def timestamp(t: int) -> int:
    return t


# /**
#  * Normalizes an app data value to a 32-byte hash.
#  * @param hashLike A hash-like value to normalize.
#  * @returns A 32-byte hash encoded as a hex-string.
#  */
# export function hashify(h: HashLike): string {
#   return typeof h === "number"
#     ? `0x${h.toString(16).padStart(64, "0")}`
#     : ethers.utils.hexZeroPad(h, 32);
# }


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


# /**
#  * Normalized representation of an {@link Order} for EIP-712 operations.
#  */
# export type NormalizedOrder = Omit<
#   Order,
#   "validTo" | "appData" | "kind" | "sellTokenBalance" | "buyTokenBalance"
# > & {
#   receiver: string;
#   validTo: number;
#   appData: string;
#   kind: "sell" | "buy";
#   sellTokenBalance: "erc20" | "external" | "internal";
#   buyTokenBalance: "erc20" | "internal";
# };

# /**
#  * Normalizes an order for hashing and signing, so that it can be used with
#  * Ethers.js for EIP-712 operations.
#  * @param hashLike A hash-like value to normalize.
#  * @returns A 32-byte hash encoded as a hex-string.
#  */
# export function normalizeOrder(order: Order): NormalizedOrder {
#   if (order.receiver === ethers.constants.AddressZero) {
#     throw new Error("receiver cannot be address(0)");
#   }

#   const normalizedOrder = {
#     ...order,
#     buyTokenBalance: normalizeBuyTokenBalance(order.buyTokenBalance),
#   };
#   return normalizedOrder;
# }

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
        "validTo": timestamp(order.validTo),
        "appData": hashify(order.appData),
        "feeAmount": order.feeAmount,
        "kind": order.kind,
        "partiallyFillable": order.partiallyFillable,
        "sellTokenBalance": order.sellTokenBalance
        if order.sellTokenBalance
        else OrderBalance.ERC20.value,
        "buyTokenBalance": normalize_buy_token_balance(order.buyTokenBalance),
    }


# /**
#  * Compute the 32-byte signing hash for the specified order.
#  *
#  * @param domain The EIP-712 domain separator to compute the hash for.
#  * @param types The order to compute the digest for.
#  * @return Hex-encoded 32-byte order digest.
#  */
# export function hashTypedData(
#   domain: TypedDataDomain,
#   types: TypedDataTypes,
#   data: Record<string, unknown>,
# ): string {
#   return ethers.utils._TypedDataEncoder.hash(domain, types, data);
# }


def hash_typed_data(domain, types, data) -> SignableMessage:
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
    return encoded_data


# /**
#  * Compute the 32-byte signing hash for the specified order.
#  *
#  * @param domain The EIP-712 domain separator to compute the hash for.
#  * @param order The order to compute the digest for.
#  * @return Hex-encoded 32-byte order digest.
#  */
# export function hashOrder(domain: TypedDataDomain, order: Order): string {
#   return hashTypedData(
#     domain,
#     { Order: ORDER_TYPE_FIELDS },
#     normalizeOrder(order),
#   );
# }


def hash_order(domain, order):
    """
    Compute the 32-byte signing hash for the specified order.

    :param domain: The EIP-712 domain separator to compute the hash for.
    :param order: The order to compute the digest for.
    :return: Hex-encoded 32-byte order digest.
    """
    return hash_typed_data(domain, ORDER_TYPE_FIELDS, normalize_order(order))


def hash_order_cancellation(domain, order_uid) -> SignableMessage:
    """
    Compute the 32-byte signing hash for the specified cancellation.

    :param domain: The EIP-712 domain separator to compute the hash for.
    :param order_uid: The unique identifier of the order to cancel.
    :return: Hex-encoded 32-byte order digest.
    """
    return hash_order_cancellations(domain, [order_uid])


def hash_order_cancellations(domain, order_uids) -> SignableMessage:
    """
    Compute the 32-byte signing hash for the specified order cancellations.

    :param domain: The EIP-712 domain separator to compute the hash for.
    :param order_uids: The unique identifiers of the orders to cancel.
    :return: Hex-encoded 32-byte order digest.
    """
    return hash_typed_data(
        domain,
        {"OrderCancellations": CANCELLATIONS_TYPE_FIELDS},
        {"orderUids": order_uids},
    )


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


# /**
#  * Computes the order UID for an order and the given owner.
#  */
# export function computeOrderUid(
#   domain: TypedDataDomain,
#   order: Order,
#   owner: string,
# ): string {
#   return packOrderUidParams({
#     orderDigest: hashOrder(domain, order),
#     owner,
#     validTo: order.validTo,
#   });
# }

# /**
#  * Compute the unique identifier describing a user order in the settlement
#  * contract.
#  *
#  * @param OrderUidParams The parameters used for computing the order's unique
#  * identifier.
#  * @returns A string that unequivocally identifies the order of the user.
#  */
# export function packOrderUidParams({
#   orderDigest,
#   owner,
#   validTo,
# }: OrderUidParams): string {
#   return ethers.utils.solidityPack(
#     ["bytes32", "address", "uint32"],
#     [orderDigest, owner, timestamp(validTo)],
#   );
# }

# /**
#  * Extracts the order unique identifier parameters from the specified bytes.
#  *
#  * @param orderUid The order UID encoded as a hexadecimal string.
#  * @returns The extracted order UID parameters.
#  */
# export function extractOrderUidParams(orderUid: string): OrderUidParams {
#   const bytes = ethers.utils.arrayify(orderUid);
#   if (bytes.length != ORDER_UID_LENGTH) {
#     throw new Error("invalid order UID length");
#   }

#   const view = new DataView(bytes.buffer);
#   return {
#     orderDigest: ethers.utils.hexlify(bytes.subarray(0, 32)),
#     owner: ethers.utils.getAddress(
#       ethers.utils.hexlify(bytes.subarray(32, 52)),
#     ),
#     validTo: view.getUint32(52),
#   };
# }
