from typing import Any, Dict
import httpx
from multiformats import CID
from collections.abc import Mapping


import json

from cowdao_cowpy.app_data.consts import DEFAULT_IPFS_READ_URI

# CID uses multibase to self-describe the encoding used (See https://github.com/multiformats/multibase)
#   - Most reference implementations (multiformats/cid or Pinata, etc) use base58btc encoding
#   - However, the backend uses base16 encoding (See https://github.com/cowprotocol/services/blob/main/crates/app-data-hash/src/lib.rs#L64)
MULTIBASE_BASE16 = "f"


def extract_digest(cid_str: str) -> str:
    cid = CID.decode(cid_str)
    return "0x" + cid.raw_digest.hex()


def sort_nested_dict(d):
    return {
        k: sort_nested_dict(v) if isinstance(v, Mapping) else v
        for k, v in sorted(d.items())
    }


def stringify_deterministic(obj):
    sorted_dict = sort_nested_dict(obj)
    return json.dumps(sorted_dict, sort_keys=True, separators=(",", ":"))


async def fetch_doc_from_cid(
    cid: str, ipfs_uri: str = DEFAULT_IPFS_READ_URI
) -> Dict[str, Any]:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{ipfs_uri}/{cid}")
        return response.json()
