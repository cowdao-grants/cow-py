from typing import Dict, Any
from web3 import Web3
from multiformats import multibase, CID

from cow_py.app_data.appDataCid import AppDataCid
from cow_py.app_data.consts import MetaDataError


class AppDataHex:
    def __init__(self, app_data_hex: str):
        self.app_data_hex = app_data_hex

    def to_cid(self) -> AppDataCid:
        cid = self._app_data_hex_to_cid()
        self._assert_cid(cid)
        return AppDataCid(cid)

    def to_cid_legacy(self) -> AppDataCid:
        cid = self._app_data_hex_to_cid_legacy()
        self._assert_cid(cid)
        return AppDataCid(cid)

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
