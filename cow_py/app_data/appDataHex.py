from web3 import Web3
from cid import make_cid
import multihash
from cow_py.app_data.appDataCid import AppDataCid
from cow_py.app_data.consts import MetaDataError


class AppDataHex:
    def __init__(self, app_data_hex: str):
        self.app_data_hex = app_data_hex

    async def to_cid(self) -> AppDataCid:
        cid = await self._app_data_hex_to_cid()
        await self._assert_cid(cid)
        return AppDataCid(cid)

    async def to_cid_legacy(self) -> AppDataCid:
        cid = await self._app_data_hex_to_cid_legacy()
        await self._assert_cid(cid)
        return AppDataCid(cid)

    async def _assert_cid(self, cid: str):
        if not cid:
            raise MetaDataError(
                f"Error getting CID from appDataHex: {self.app_data_hex}"
            )

    async def _app_data_hex_to_cid(self) -> str:
        hash_bytes = Web3.to_bytes(hexstr=self.app_data_hex)
        mh = multihash.encode(hash_bytes, 'keccak-256')
        cid = make_cid(1, 'raw', mh)
        return str(cid)

    async def _app_data_hex_to_cid_legacy(self) -> str:
        hash_bytes = Web3.to_bytes(hexstr=self.app_data_hex)
        mh = multihash.encode(hash_bytes, 'sha2-256')
        cid = make_cid(0, 'dag-pb', mh)
        return str(cid)