"""Conformance of cow-py order hashing and signing against cowprotocol/services.

The fixture is generated from ``cowprotocol/services`` ``model::order`` and
``model::signature`` at the commit recorded in ``services_sha`` (see
``cowdao-grants/cow-rs`` ``tools/conformance-gen``). Every value below is what
the orderbook itself computes, so a mismatch here is an order the orderbook
would reject or attribute to the wrong owner.
"""

import json
from pathlib import Path

import pytest
from eth_account import Account
from eth_account.messages import encode_typed_data
from eth_utils.conversions import to_hex
from eth_utils.crypto import keccak
from web3 import Web3

from cowdao_cowpy.contracts.domain import TypedDataDomain
from cowdao_cowpy.contracts.order import (
    ORDER_TYPE_FIELDS,
    Order,
    compute_order_uid,
    hash_order,
    normalize_order,
)
from cowdao_cowpy.contracts.sign import SigningScheme, sign_order

FIXTURE = Path(__file__).parent / "fixtures" / "conformance_vectors.v1.json"
VECTORS = json.loads(FIXTURE.read_text())

# Hardhat/Anvil account 0. Test key only; it is the signer recorded in the fixture.
TEST_KEY = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
SIGNER = Account.from_key(TEST_KEY)

DOMAIN = TypedDataDomain(
    name="Gnosis Protocol",
    version="v2",
    chainId=VECTORS["chain_id"],
    verifyingContract=Web3.to_checksum_address(VECTORS["settlement"]),
)

ETHSIGN_PREFIX = b"\x19Ethereum Signed Message:\n32"


def _order(v):
    receiver = v["receiver"]
    receiver = (
        ""
        if receiver is None or int(receiver, 16) == 0
        else Web3.to_checksum_address(receiver)
    )
    return Order(
        sell_token=Web3.to_checksum_address(v["sell_token"]),
        buy_token=Web3.to_checksum_address(v["buy_token"]),
        receiver=receiver,
        sell_amount=v["sell_amount"],
        buy_amount=v["buy_amount"],
        valid_to=v["valid_to"],
        app_data=v["app_data"],
        fee_amount=v["fee_amount"],
        kind=v["kind"],
        partially_fillable=v["partially_fillable"],
        sell_token_balance=v["sell_token_balance"],
        buy_token_balance=v["buy_token_balance"],
    )


def _sig_hex(sig):
    return "0x" + sig["r"][2:] + sig["s"][2:] + f"{sig['v']:02x}"


def test_fixture_signer_matches_test_key():
    assert SIGNER.address.lower() == VECTORS["signer"]
    assert len(VECTORS["vectors"]) == VECTORS["order_vector_count"]


@pytest.mark.parametrize(
    "v", VECTORS["vectors"], ids=[v["id"] for v in VECTORS["vectors"]]
)
def test_order_hashing_matches_services(v):
    order = _order(v)
    signable = encode_typed_data(
        domain_data=DOMAIN.to_dict(),
        message_types={"Order": ORDER_TYPE_FIELDS},
        message_data=normalize_order(order),
    )
    assert to_hex(signable.header) == v["domain_separator"]
    assert to_hex(signable.body) == v["hash_struct"]
    assert to_hex(hash_order(DOMAIN, order)) == v["eip712_digest"]
    assert compute_order_uid(DOMAIN, order, SIGNER.address).lower() == v["uid"]


@pytest.mark.parametrize(
    "v", VECTORS["vectors"], ids=[v["id"] for v in VECTORS["vectors"]]
)
def test_eip712_signature_matches_services(v):
    order = _order(v)
    sig = sign_order(DOMAIN, order, SIGNER, SigningScheme.EIP712)
    assert sig.scheme == SigningScheme.EIP712
    assert sig.data.lower() == _sig_hex(v["eip712_signature"]).lower()
    recovered = Account._recover_hash(hash_order(DOMAIN, order), signature=sig.data)
    assert recovered.lower() == v["eip712_recovered_owner"]


@pytest.mark.parametrize(
    "v", VECTORS["vectors"], ids=[v["id"] for v in VECTORS["vectors"]]
)
def test_ethsign_signature_matches_services(v):
    """services signs keccak("\\x19Ethereum Signed Message:\\n32" || eip712_digest) for EthSign."""
    order = _order(v)
    eip712_digest = bytes(hash_order(DOMAIN, order))
    ethsign_digest = keccak(ETHSIGN_PREFIX + eip712_digest)
    assert to_hex(ethsign_digest) == v["ethsign_digest"]

    sig = sign_order(DOMAIN, order, SIGNER, SigningScheme.ETHSIGN)
    assert sig.scheme == SigningScheme.ETHSIGN
    assert sig.data.lower() == _sig_hex(v["ethsign_signature"]).lower()
    recovered = Account._recover_hash(ethsign_digest, signature=sig.data)
    assert recovered.lower() == v["ethsign_recovered_owner"]
