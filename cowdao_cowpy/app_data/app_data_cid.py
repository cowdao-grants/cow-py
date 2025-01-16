from typing import Any, Dict

from cowdao_cowpy.app_data.consts import DEFAULT_IPFS_READ_URI
from cowdao_cowpy.app_data.utils import extract_digest, fetch_doc_from_cid


class AppDataCid:
    def __init__(self, app_data_cid: str):
        self.app_data_cid = app_data_cid

    async def to_doc(self, ipfs_uri: str = DEFAULT_IPFS_READ_URI) -> Dict[str, Any]:
        return await fetch_doc_from_cid(self.app_data_cid, ipfs_uri)

    def to_hex(self) -> str:
        return extract_digest(self.app_data_cid)
