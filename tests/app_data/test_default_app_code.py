import json
import subprocess
import sys

from eth_utils.crypto import keccak

from cowdao_cowpy.app_data.consts import DEFAULT_APP_CODE, DEFAULT_APP_DATA_DOC
from cowdao_cowpy.app_data.utils import (
    DEFAULT_APP_DATA_HASH,
    PartnerFee,
    generate_app_data,
)


def independent_hash(doc: dict) -> str:
    # Deliberately re-derives the hash without using cowdao_cowpy helpers so a
    # regression in the canonicalization or hashing code cannot cancel out.
    canonical = json.dumps(doc, sort_keys=True, separators=(",", ":"))
    return "0x" + keccak(canonical.encode("utf-8")).hex()


def test_default_app_data_hash_matches_independent_computation():
    assert DEFAULT_APP_DATA_HASH == independent_hash(DEFAULT_APP_DATA_DOC)


def test_generate_app_data_defaults_reproduce_module_constant():
    create_app_data = generate_app_data()
    assert create_app_data.app_data_hash.root == DEFAULT_APP_DATA_HASH
    assert create_app_data.app_data_object.fullAppData is not None
    full_app_data = json.loads(create_app_data.app_data_object.fullAppData.root)
    assert full_app_data == DEFAULT_APP_DATA_DOC


def test_default_doc_shape():
    assert DEFAULT_APP_CODE == "cowdao_cowpy"
    assert DEFAULT_APP_DATA_DOC["appCode"] == DEFAULT_APP_CODE
    assert set(DEFAULT_APP_DATA_DOC) == {"appCode", "metadata", "version"}


def test_default_app_data_hash_format():
    assert DEFAULT_APP_DATA_HASH.startswith("0x")
    assert len(DEFAULT_APP_DATA_HASH) == 66
    int(DEFAULT_APP_DATA_HASH, 16)


def test_partner_fee_serializes_as_object():
    create_app_data = generate_app_data(
        partner_fee=PartnerFee(bps=100, recipient="0x" + "11" * 20)
    )
    assert create_app_data.app_data_object.fullAppData is not None
    full_app_data = json.loads(create_app_data.app_data_object.fullAppData.root)
    assert full_app_data["metadata"]["partnerFee"] == {
        "bps": 100,
        "recipient": "0x" + "11" * 20,
    }


def test_generate_app_data_does_not_mutate_default_doc():
    generate_app_data(
        graffiti="custom-graffiti",
        referrer_address="0x" + "22" * 20,
        partner_fee=PartnerFee(bps=50, recipient="0x" + "33" * 20),
    )
    assert "partnerFee" not in DEFAULT_APP_DATA_DOC["metadata"]
    assert "referrer" not in DEFAULT_APP_DATA_DOC["metadata"]
    assert DEFAULT_APP_DATA_DOC["metadata"]["utm"]["utmContent"] != "custom-graffiti"


def test_import_performs_no_network_io():
    # Run in a subprocess because this package is already imported in-process.
    code = (
        "import socket\n"
        "class _Blocked(socket.socket):\n"
        "    def __init__(self, *args, **kwargs):\n"
        "        raise AssertionError('network access attempted during import')\n"
        "socket.socket = _Blocked\n"
        "socket.create_connection = _Blocked\n"
        "import cowdao_cowpy\n"
        "from cowdao_cowpy.app_data.utils import DEFAULT_APP_DATA_HASH\n"
        "assert DEFAULT_APP_DATA_HASH.startswith('0x')\n"
        "print('IMPORT_OK')\n"
    )
    result = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True, timeout=120
    )
    assert result.returncode == 0, result.stderr
    assert "IMPORT_OK" in result.stdout
