import asyncio
from typing import Any, Dict
from cowdao_cowpy.order_book.api import OrderBookApi
from cowdao_cowpy.order_book.config import OrderBookAPIConfigFactory
from cowdao_cowpy.order_book.generated.model import AppData, AppDataHash, AppDataObject
import httpx
from multiformats import CID
from collections.abc import Mapping
from cowdao_cowpy.common.api.api_base import Envs
from cowdao_cowpy.common.config import SupportedChainId

from web3 import Web3

from dataclasses import asdict, dataclass
import json

from cowdao_cowpy.common.api.errors import UnexpectedResponseError
from cowdao_cowpy.app_data.consts import (
    DEFAULT_APP_CODE,
    DEFAULT_APP_DATA_DOC,
    DEFAULT_GRAFFITI,
    DEFAULT_IPFS_READ_URI,
)

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
    return Web3.keccak(data).hex()


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
    app_code: str = None,
    partner_fee: PartnerFee = None,
    referrer_address: str = None,
    graffiti: str | None = None,
) -> CreateAppData:
    app_data_doc = DEFAULT_APP_DATA_DOC.copy()
    if graffiti:
        app_data_doc["metadata"]["utm"]["utmContent"] = graffiti

    if referrer_address:
        app_data_doc["metadata"]["referrer"] = {
            "address": referrer_address,
        }
    if partner_fee:
        app_data_doc["metadata"]["partnerFee"] = (asdict(partner_fee),)

    if app_code:
        app_data_doc["appCode"] = app_code

    stringified_data = stringify_deterministic(app_data_doc)
    app_data_hash = keccak256(stringified_data.encode("utf-8"))
    return CreateAppData(
        AppDataObject(fullAppData=AppData(stringified_data)),
        AppDataHash(root=app_data_hash),
    )


def check_app_data_exists(orderbook: OrderBookApi, app_data_hash: AppDataHash) -> bool:
    try:
        # Attempt to fetch the app data from the orderbook
        asyncio.run(orderbook.get_app_data(app_data_hash))
    except Exception as e:  # noqa
        print(f"App data not found: {e}")
        return False
    return True


def build_and_post_app_data(
    orderbook: OrderBookApi,
    app_code: str | None = None,
    referrer_address: str | None = None,
    partner_fee: PartnerFee | None = None,
    graffiti: str | None = None,
) -> str:
    create_app_data = generate_app_data(
        app_code=app_code,
        referrer_address=referrer_address,
        partner_fee=partner_fee,
        graffiti=graffiti,
    )
    if not check_app_data_exists(orderbook, create_app_data.app_data_hash):
        print("App data does not exist, uploading... to ", orderbook.config.chain_id)
        asyncio.run(
            orderbook.put_app_data(
                create_app_data.app_data_object, create_app_data.app_data_hash
            )
        )
    return create_app_data.app_data_hash.root


def build_all_app_codes(
    env: Envs = "prod",
    app_code: str = DEFAULT_APP_CODE,
    graffiti: str | None = DEFAULT_GRAFFITI,
    referrer_address: str | None = None,
    partner_fee: PartnerFee | None = None,
) -> str:
    """
    Builds and posts app data for all supported chain IDs.
    """
    for chain_id in SupportedChainId:
        order_book_api = OrderBookApi(
            OrderBookAPIConfigFactory.get_config(env, chain_id)
        )
        app_data_hash = build_and_post_app_data(
            order_book_api, app_code, referrer_address, partner_fee, graffiti
        )
    return app_data_hash  # type: ignore


try:
    DEFAULT_APP_DATA_HASH = build_all_app_codes()
except (UnexpectedResponseError, ValueError) as e:
    print(f"Error building default app data: {e}")
    DEFAULT_APP_DATA_HASH = "0x971c41b97f59534448ab833b0d83f755a4bc5c29f92b01776faa3699fcb0eeae"  # fallback to known hash
