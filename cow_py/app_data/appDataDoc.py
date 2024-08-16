from typing import Dict, Any, TypedDict, Optional

import httpx

from cow_py.app_data.consts import DEFAULT_IPFS_WRITE_URI, MetaDataError
from cow_py.app_data.utils import extract_digest, stringify_deterministic


class IpfsUploadResult(TypedDict):
    appData: str
    cid: str


class PinataPinResponse(TypedDict):
    IpfsHash: str
    PinSize: int
    Timestamp: str


class Ipfs(TypedDict):
    writeUri: str
    pinataApiKey: str
    pinataApiSecret: str


class AppDataDoc:
    def __init__(self, app_data_doc: Dict[str, Any]):
        self.app_data_doc = app_data_doc

    # TODO: Missing test
    async def upload_to_ipfs_legacy(
        self, ipfs_config: Ipfs
    ) -> Optional[IpfsUploadResult]:
        """
        Uploads a appDocument to IPFS

        @deprecated Pinata IPFS automatically pins the uploaded document using some implicit encoding and hashing algorithm.
        This method is not used anymore to make it more explicit these parameters and therefore less dependent on the default implementation of Pinata

        @param app_data_doc Document to upload
        @param ipfs_config keys to access the IPFS API

        @returns the IPFS CID v0 of the content
        """
        pin_response = await self._pin_json_in_pinata_ipfs(
            self.app_data_doc, ipfs_config
        )
        cid = pin_response["IpfsHash"]
        return {
            "appData": extract_digest(cid),
            "cid": cid,
        }

    async def _pin_json_in_pinata_ipfs(
        self, file: Any, ipfs_config: Ipfs
    ) -> PinataPinResponse:
        write_uri = ipfs_config.get("writeUri", DEFAULT_IPFS_WRITE_URI)
        pinata_api_key = ipfs_config.get("pinataApiKey", "")
        pinata_api_secret = ipfs_config.get("pinataApiSecret", "")

        if not pinata_api_key or not pinata_api_secret:
            raise MetaDataError("You need to pass IPFS api credentials.")

        body = stringify_deterministic(
            {
                "pinataContent": file,
                "pinataMetadata": {"name": "appData"},
            }
        )

        pinata_url = f"{write_uri}/pinning/pinJSONToIPFS"
        headers = {
            "Content-Type": "application/json",
            "pinata_api_key": pinata_api_key,
            "pinata_secret_api_key": pinata_api_secret,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(pinata_url, json=body, headers=headers)
            data = response.json()
            if response.status_code != 200:
                raise Exception(
                    data.get("error", {}).get("details") or data.get("error")
                )
            return data
