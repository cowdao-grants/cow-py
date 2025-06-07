from typing import Any, Dict
from cowdao_cowpy.order_book.generated.model import AppData, AppDataHash, AppDataObject
import httpx
from multiformats import CID
from collections.abc import Mapping

import sha3

from dataclasses import asdict, dataclass
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


def keccak256(data: bytes) -> str:
    return sha3.keccak_256(data).hexdigest()


async def fetch_doc_from_cid(
    cid: str, ipfs_uri: str = DEFAULT_IPFS_READ_URI
) -> Dict[str, Any]:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{ipfs_uri}/{cid}")
        return response.json()


@dataclass
class CreateAppData:
    app_data_object: AppDataObject
    app_data_hash: AppDataHash


@dataclass
class PartnerFee:
    bps: int
    recipient: str


@dataclass
class QuoteFee:
    slippageBips: int = 1
    version: str = "0.2.0"


def generate_app_data(
    app_code: str,
    partner_fee: PartnerFee = None,
    referrer_address: str = None,
    version: str = "1.3.0",
    hooks_version: str = "0.1.0",
) -> CreateAppData:
    app_data_doc = {
        "appCode": app_code,
        "metadata": {
            "hooks": {
                "version": hooks_version,
            },
        },
        "version": version,
    }  # compact encoding to match JS behavior

    if referrer_address:
        app_data_doc["metadata"]["referrer"] = {
            "address": referrer_address,
        }
    if partner_fee:
        app_data_doc["metadata"]["partnerFee"] = (asdict(partner_fee),)

    stringified_data = stringify_deterministic(app_data_doc)
    app_data_hash = keccak256(stringified_data.encode("utf-8"))
    return CreateAppData(
        AppDataObject(fullAppData=AppData(stringified_data)),
        AppDataHash(root=app_data_hash),
    )
