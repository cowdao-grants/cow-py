import pytest
from eth_account.messages import SignableMessage
from eth_account.signers.local import LocalAccount
from eth_utils.conversions import to_hex
from web3 import EthereumTesterProvider, Web3

from cow_py.contracts.order import hash_order_cancellation

from cow_py.contracts.sign import SigningScheme, sign_order, sign_order_cancellation

from .conftest import SAMPLE_ORDER

w3 = Web3(EthereumTesterProvider())


def patched_sign_message_builder(account: LocalAccount):
    def sign_message(message):
        # Determine the correct message format
        if isinstance(message, SignableMessage):
            message_to_hash = message.body
        elif isinstance(message, (bytes, str)):
            message_to_hash = message
        else:
            raise TypeError("Unsupported message type for signing.")

        # Hash and sign the message
        message_hash = Web3.solidity_keccak(["bytes"], [message_to_hash])
        signature = account.signHash(message_hash)
        r, s, v = signature["r"], signature["s"], signature["v"]

        # Adjust v to be 27 or 28
        v_adjusted = v + 27 if v < 27 else v

        # Concatenate the signature components into a hex string
        signature_hex = to_hex(r)[2:] + to_hex(s)[2:] + hex(v_adjusted)[2:]

        return signature_hex

    return sign_message


@pytest.mark.asyncio
@pytest.mark.parametrize("scheme", [SigningScheme.EIP712, SigningScheme.ETHSIGN])
async def test_sign_order(monkeypatch, scheme):
    signer = w3.eth.account.create()

    patched_sign_message = patched_sign_message_builder(signer)

    # Use monkeypatch to temporarily replace sign_message
    monkeypatch.setattr(signer, "sign_message", patched_sign_message)

    domain = {"name": "test"}
    signed_order = sign_order(domain, SAMPLE_ORDER, signer, scheme)

    # Extract 'v' value from the last two characters of the signature
    v = signed_order.data[-2:]

    assert v in ["1b", "1c"]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "scheme", [SigningScheme.EIP712.value, SigningScheme.ETHSIGN.value]
)
async def test_sign_order_cancellation(scheme):
    signer = w3.eth.account.create()
    domain = {"name": "test"}
    order_uid = "0x" + "2a" * 56

    signature_data = sign_order_cancellation(domain, order_uid, signer, scheme)
    order_hash = hash_order_cancellation(domain, order_uid)

    assert (
        w3.eth.account._recover_hash(order_hash, signature=signature_data.data)
        == signer.address
    )
