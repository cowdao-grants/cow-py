from typing import Dict, Any
from web3 import Web3
from multiformats import multibase, CID

from cow_py.app_data.appDataCid import AppDataCid
from cow_py.app_data.appDataDoc import AppDataDoc
from cow_py.app_data.consts import DEFAULT_IPFS_READ_URI, MetaDataError
from cow_py.app_data.utils import fetch_doc_from_cid


class AppDataHex:
    def __init__(self, app_data_hex: str):
        self.app_data_hex = app_data_hex

    def to_cid(self) -> str:
        cid = self._app_data_hex_to_cid()
        self._assert_cid(cid)
        return cid

    def to_cid_legacy(self) -> str:
        cid = self._app_data_hex_to_cid_legacy()
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

    async def to_doc_legacy(
        self, ipfs_uri: str = DEFAULT_IPFS_READ_URI
    ) -> Dict[str, Any]:
        try:
            cid = self.to_cid_legacy()
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
                "version": 0x01,  # CIDv1
                "multicodec": 0x55,  # Raw codec
                "hashing_algorithm": 0x1B,  # keccak hash algorithm
                "hashing_length": 32,  # keccak hash length (0x20 = 32)
                "multihash_hex": self.app_data_hex,  # 32 bytes of the keccak256 hash
            }
        )
        return multibase.encode(cid_bytes, "base16")

    def _app_data_hex_to_cid_legacy(self) -> str:
        cid_bytes = self._to_cid_bytes(
            {
                "version": 0x01,  # CIDv1
                "multicodec": 0x70,  # dag-pb
                "hashing_algorithm": 0x12,  # sha2-256 hash algorithm
                "hashing_length": 32,  # SHA-256 length (0x20 = 32)
                "multihash_hex": self.app_data_hex,  # 32 bytes of the sha2-256 hash
            }
        )
        return str(CID.decode(cid_bytes).set(version=0))

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
