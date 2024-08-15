from typing import Union
from multiformats import CID
from multiformats import base16, base58btc
import binascii
import json

# CID uses multibase to self-describe the encoding used (See https://github.com/multiformats/multibase)
#   - Most reference implementations (multiformats/cid or Pinata, etc) use base58btc encoding
#   - However, the backend uses base16 encoding (See https://github.com/cowprotocol/services/blob/main/crates/app-data-hash/src/lib.rs#L64)
MULTIBASE_BASE16 = "f"


def parse_cid(ipfs_hash: str) -> CID:
    decoder = get_decoder(ipfs_hash)
    return CID.decode(ipfs_hash)


def decode_cid(bytes_: bytes) -> CID:
    return CID.decode(bytes_)


def get_decoder(ipfs_hash: str) -> Union[base16, base58btc]:
    if ipfs_hash[0] == MULTIBASE_BASE16:
        # Base 16 encoding
        return base16
    # Use default decoder (base58btc)
    return base58btc


def extract_digest(cid: str) -> str:
    cid_details = parse_cid(cid)
    digest = cid_details.multihash.digest
    return f"0x{binascii.hexlify(digest).decode('ascii')}"


def stringify_deterministic(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))
