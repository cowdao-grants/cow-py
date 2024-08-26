from typing import Dict, Any, TypedDict, Optional

from multiformats import CID, multihash
from pinatapy import PinataPy
from eth_utils import keccak, to_bytes

from cow_py.app_data.app_data_hex import AppDataHex
from cow_py.app_data.consts import DEFAULT_APP_DATA_DOC
from cow_py.app_data.utils import extract_digest, stringify_deterministic


class IpfsUploadResult(TypedDict):
    appData: str
    cid: str


class PinataConfig(TypedDict):
    pinata_api_key: str
    pinata_api_secret: str


class AppDataDoc:
    def __init__(self, app_data_doc: Dict[str, Any] = {}):
        self.app_data_doc = {**DEFAULT_APP_DATA_DOC, **app_data_doc}

    # TODO: make this async
    def upload_to_ipfs_legacy(
        self, ipfs_config: PinataConfig
    ) -> Optional[IpfsUploadResult]:
        """
        Uploads a appDocument to IPFS

        @deprecated Pinata IPFS automatically pins the uploaded document using some implicit encoding and hashing algorithm.
        This method is not used anymore to make it more explicit these parameters and therefore less dependent on the default implementation of Pinata

        @param app_data_doc Document to upload
        @param ipfs_config keys to access the IPFS API

        @returns the IPFS CID v0 of the content
        """
        pinata = PinataPy(
            ipfs_config.get("pinata_api_key", ""),
            ipfs_config.get("pinata_api_secret", ""),
        )
        pin_response = pinata.pin_json_to_ipfs(
            stringify_deterministic(self.app_data_doc)
        )
        cid = pin_response["IpfsHash"]
        return {
            "appData": extract_digest(cid),
            "cid": cid,
        }

    def to_cid(self):
        full_app_data_json = stringify_deterministic(self.app_data_doc)

        # TODO: add validation of app data
        app_data_bytes = to_bytes(text=full_app_data_json)
        appDataHex = AppDataHex(keccak(app_data_bytes).hex())
        return appDataHex.to_cid()

    def to_cid_legacy(self) -> str:
        full_app_data_json = stringify_deterministic(self.app_data_doc)

        # TODO: add validation of app data
        data_bytes = to_bytes(text=full_app_data_json)
        sha2_256 = multihash.get("sha2-256")
        mh = sha2_256.digest(data_bytes)
        cid = CID("base58btc", 0, "dag-pb", mh)

        return str(cid)
