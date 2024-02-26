from eth_account.signers.local import LocalAccount
from eth_account.messages import encode_typed_data
from typing import List, NamedTuple, Union
from eth_utils.conversions import to_hex
from eth_utils.crypto import keccak
from web3 import Web3
from enum import IntEnum

from cow_py.contracts.order import (
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


class EcdsaSignature(NamedTuple):
    scheme: SigningScheme
    data: str


class Eip1271SignatureData(NamedTuple):
    verifier: str
    signature: bytes


class Eip1271Signature(NamedTuple):
    scheme: SigningScheme
    data: Eip1271SignatureData


class PreSignSignature(NamedTuple):
    scheme: SigningScheme
    data: str


Signature = Union[EcdsaSignature, Eip1271Signature, PreSignSignature]


def ecdsa_sign_typed_data(
    scheme, owner: LocalAccount, domain, message_types, data
) -> str:
    if scheme == SigningScheme.EIP712:
        encoded_message = encode_typed_data(
            domain_data=domain, message_types=message_types, message_data=data
        )
    elif scheme == SigningScheme.ETHSIGN:
        encoded_message = hash_typed_data(domain, message_types, data)
    else:
        raise ValueError("Invalid signing scheme")

    return owner.sign_message(encoded_message)


def sign_order(
    domain, order: Order, owner: LocalAccount, scheme: SigningScheme
) -> EcdsaSignature:
    normalized_order = normalize_order(order)
    signed_data = ecdsa_sign_typed_data(
        scheme, owner, domain, {"Order": ORDER_TYPE_FIELDS}, normalized_order
    )
    return EcdsaSignature(
        scheme=scheme,
        data=signed_data,
    )


def sign_order_cancellation(domain, order_uid: Union[str, bytes], owner, scheme):
    return sign_order_cancellations(domain, [order_uid], owner, scheme)


def sign_order_cancellations(
    domain, order_uids: List[Union[str, bytes]], owner, scheme
):
    data = {"orderUids": order_uids}
    types = {"OrderCancellations": CANCELLATIONS_TYPE_FIELDS}

    signed_data = ecdsa_sign_typed_data(scheme, owner, domain, types, data)

    return {"scheme": scheme, "data": signed_data}


def encode_eip1271_signature_data(verifier, signature):
    return Web3.solidity_keccak(["address", "bytes"], [verifier, signature])


def decode_eip1271_signature_data(signature):
    arrayified_signature = bytes.fromhex(signature[2:])  # Removing '0x'
    verifier = Web3.to_checksum_address(arrayified_signature[:20].hex())
    return Eip1271SignatureData(verifier, arrayified_signature[20:])
