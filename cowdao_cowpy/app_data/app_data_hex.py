from typing import Dict, Any
from web3 import Web3
from multiformats import multibase

from cowdao_cowpy.app_data.consts import DEFAULT_IPFS_READ_URI, MetaDataError
from cowdao_cowpy.app_data.utils import fetch_doc_from_cid

CID_V1_PREFIX = 0x01
CID_RAW_MULTICODEC = 0x55
KECCAK_HASHING_ALGORITHM = 0x1B
KECCAK_HASHING_LENGTH = 32
CID_DAG_PB_MULTICODEC = 0x70
SHA2_256_HASHING_ALGORITHM = 0x12
SHA2_256_HASHING_LENGTH = 32


class AppDataHex:
    def __init__(self, app_data_hex: str):
        self.app_data_hex = app_data_hex

    def to_cid(self) -> str:
        cid = self._app_data_hex_to_cid()
        self._assert_cid(cid)
        return cid

    async def to_doc(self, ipfs_uri: str = DEFAULT_IPFS_READ_URI) -> Dict[str, Any]:
        try:
            cid = self.to_cid()
            return await fetch_doc_from_cid(cid, ipfs_uri)
        except Exception as e:
            raise MetaDataError(
                f"Unexpected error decoding AppData: appDataHex={self.app_data_hex}, message={e}"
            )

    def _assert_cid(self, cid: str):
        if not cid:
            raise MetaDataError(
                f"Error getting CID from appDataHex: {self.app_data_hex}"
            )

    def _app_data_hex_to_cid(self) -> str:
        cid_bytes = self._to_cid_bytes(
            {
                "version": CID_V1_PREFIX,
                "multicodec": CID_RAW_MULTICODEC,
                "hashing_algorithm": KECCAK_HASHING_ALGORITHM,
                "hashing_length": KECCAK_HASHING_LENGTH,
                "multihash_hex": self.app_data_hex,
            }
        )
        return multibase.encode(cid_bytes, "base16")

    def _to_cid_bytes(self, params: Dict[str, Any]) -> bytes:
        hash_bytes = Web3.to_bytes(hexstr=params["multihash_hex"])
        cid_prefix = bytes(
            [
                params["version"],
                params["multicodec"],
                params["hashing_algorithm"],
                params["hashing_length"],
            ]
        )
        return cid_prefix + hash_bytes
