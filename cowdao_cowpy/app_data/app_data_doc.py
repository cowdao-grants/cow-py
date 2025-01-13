from typing import Dict, Any

from eth_utils.crypto import keccak

from cowdao_cowpy.app_data.app_data_hex import AppDataHex
from cowdao_cowpy.app_data.consts import DEFAULT_APP_DATA_DOC
from cowdao_cowpy.app_data.utils import stringify_deterministic


class AppDataDoc:
    def __init__(
        self, app_data_doc: Dict[str, Any] = {}, app_data_doc_string: str = ""
    ):
        self.app_data_doc = {**DEFAULT_APP_DATA_DOC, **app_data_doc}
        self.app_data_doc_string = app_data_doc_string

    def to_string(self) -> str:
        if self.app_data_doc_string:
            return self.app_data_doc_string
        return stringify_deterministic(self.app_data_doc)

    def to_hex(self) -> str:
        # TODO: add validation of app data
        full_app_data_json = self.to_string()
        data_bytes = full_app_data_json.encode("utf-8")
        return "0x" + keccak(data_bytes).hex()

    def to_cid(self) -> str:
        appDataHex = AppDataHex(self.to_hex()[2:])
        return appDataHex.to_cid()
