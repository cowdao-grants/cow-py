import pytest
from eth_account import Account
from eth_account.messages import encode_defunct
from eth_typing import HexStr
from eth_utils.crypto import keccak
from web3 import EthereumTesterProvider, Web3

from cowdao_cowpy.contracts.order import hash_order, hash_order_cancellation
from cowdao_cowpy.contracts.sign import (
    SigningScheme,
    sign_order,
    sign_order_cancellation,
)

from .conftest import SAMPLE_DOMAIN, SAMPLE_ORDER

w3 = Web3(EthereumTesterProvider())

ETHSIGN_PREFIX = b"\x19Ethereum Signed Message:\n32"


def _signed_digest(digest: bytes, scheme: SigningScheme) -> bytes:
    """The 32 bytes an ECDSA signature of ``digest`` must recover against."""
    if scheme == SigningScheme.ETHSIGN:
        return keccak(ETHSIGN_PREFIX + digest)
    return digest


@pytest.mark.parametrize("scheme", [SigningScheme.EIP712, SigningScheme.ETHSIGN])
def test_sign_order(scheme):
    signer = w3.eth.account.create()

    signed_order = sign_order(SAMPLE_DOMAIN, SAMPLE_ORDER, signer, scheme)

    assert signed_order.scheme == scheme
    assert signed_order.data[-2:] in ["1b", "1c"]

    digest = bytes(hash_order(SAMPLE_DOMAIN, SAMPLE_ORDER))
    recovered = Account._recover_hash(
        _signed_digest(digest, scheme), signature=signed_order.data
    )
    assert recovered == signer.address


def test_ethsign_order_signature_is_an_eth_sign_of_the_eip712_digest():
    """ETHSIGN must equal what a wallet's ``eth_sign`` of the EIP-712 digest returns."""
    signer = w3.eth.account.create()
    digest = bytes(hash_order(SAMPLE_DOMAIN, SAMPLE_ORDER))

    expected = signer.sign_message(encode_defunct(primitive=digest)).signature
    actual = sign_order(SAMPLE_DOMAIN, SAMPLE_ORDER, signer, SigningScheme.ETHSIGN)

    assert actual.data == Web3.to_hex(expected)


@pytest.mark.parametrize(
    "scheme", [SigningScheme.EIP712.value, SigningScheme.ETHSIGN.value]
)
def test_sign_order_cancellation(scheme):
    signer = w3.eth.account.create()
    order_uid = "0x" + "2a" * 56

    signature_data = sign_order_cancellation(SAMPLE_DOMAIN, order_uid, signer, scheme)
    order_hash = Web3.to_bytes(
        hexstr=HexStr(hash_order_cancellation(SAMPLE_DOMAIN, order_uid))
    )

    assert (
        w3.eth.account._recover_hash(
            _signed_digest(order_hash, SigningScheme(scheme)),
            signature=signature_data.data,
        )
        == signer.address
    )
