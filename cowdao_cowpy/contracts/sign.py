from dataclasses import dataclass
from enum import IntEnum
from typing import Any, Dict, List, Union

from eth_account import Account
from eth_account.datastructures import SignedMessage
from eth_account.signers.local import LocalAccount
from eth_typing import ChecksumAddress
from eth_utils.conversions import to_hex
from eth_utils.crypto import keccak
from web3 import Web3

from cowdao_cowpy.contracts.domain import TypedDataDomain
from cowdao_cowpy.contracts.order import (
    CANCELLATIONS_TYPE_FIELDS,
    ORDER_TYPE_FIELDS,
    Order,
    hash_typed_data,
    normalize_order,
)

EIP1271_MAGICVALUE = to_hex(keccak(text="isValidSignature(bytes32,bytes)"))[:10]
PRE_SIGNED = to_hex(keccak(text="GPv2Signing.Scheme.PreSign"))


class SigningScheme(IntEnum):
    # The EIP-712 typed data signing scheme. This is the preferred scheme as it
    # provides more infomation to wallets performing the signature on the data
    # being signed.
    #
    # https://github.com/ethereum/EIPs/blob/master/EIPS/eip-712.md#definition-of-domainseparator
    EIP712 = 0b00
    # Message signed using eth_sign RPC call.
    ETHSIGN = 0b01
    # Smart contract signatures as defined in EIP-1271.
    EIP1271 = 0b10
    # Pre-signed order.
    PRESIGN = 0b11


@dataclass
class EcdsaSignature:
    scheme: SigningScheme
    data: str

    def to_string(self) -> str:
        return self.data if self.data.startswith("0x") else f"0x{self.data}"


@dataclass
class Eip1271SignatureData:
    verifier: str
    signature: bytes

    def to_string(self) -> str:
        hex_data = str(self.signature.hex())
        return hex_data if hex_data.startswith("0x") else f"0x{hex_data}"


@dataclass
class Eip1271Signature:
    scheme: SigningScheme
    data: Eip1271SignatureData

    def to_string(self) -> str:
        return self.data.to_string()


@dataclass
class PreSignSignature:
    scheme: SigningScheme
    data: str

    def to_string(self) -> str:
        return self.data if self.data.startswith("0x") else f"0x{self.data}"


Signature = Union[EcdsaSignature, Eip1271Signature, PreSignSignature]


def ecdsa_sign_typed_data(
    owner: LocalAccount,
    domain_data: TypedDataDomain,
    message_types: Dict[str, Any],
    message_data: Dict[str, Any],
) -> SignedMessage:
    return Account._sign_hash(
        hash_typed_data(domain_data, message_types, message_data), owner.key
    )


def sign_order(
    domain: TypedDataDomain, order: Order, owner: LocalAccount, scheme: SigningScheme
) -> EcdsaSignature:
    normalized_order = normalize_order(order)
    signed_data = ecdsa_sign_typed_data(
        owner, domain, {"Order": ORDER_TYPE_FIELDS}, normalized_order
    )
    return EcdsaSignature(
        scheme=scheme,
        data=signed_data.signature.hex(),
    )


def sign_order_cancellation(
    domain: TypedDataDomain,
    order_uid: Union[str, bytes],
    owner: LocalAccount,
    scheme: SigningScheme,
):
    return sign_order_cancellations(domain, [order_uid], owner, scheme)


def sign_order_cancellations(
    domain: TypedDataDomain,
    order_uids: List[Union[str, bytes]],
    owner: LocalAccount,
    scheme: SigningScheme,
):
    data = {"orderUids": order_uids}
    types = {"OrderCancellations": CANCELLATIONS_TYPE_FIELDS}

    signed_data = ecdsa_sign_typed_data(owner, domain, types, data)

    return EcdsaSignature(scheme=scheme, data=signed_data.signature.hex())


def encode_eip1271_signature_data(verifier: ChecksumAddress, signature: str) -> bytes:
    return Web3.solidity_keccak(["address", "bytes"], [verifier, signature])


def decode_eip1271_signature_data(signature: str) -> Eip1271SignatureData:
    arrayified_signature = bytes.fromhex(signature[2:])  # Removing '0x'
    verifier = Web3.to_checksum_address(arrayified_signature[:20].hex())
    return Eip1271SignatureData(verifier, arrayified_signature[20:])
