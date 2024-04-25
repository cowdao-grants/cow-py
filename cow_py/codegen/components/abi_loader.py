import json
from abc import ABC, abstractmethod
from typing import Any, List


class AbiLoader(ABC):
    @abstractmethod
    def load_abi(self) -> List[Any]:
        return []


class FileAbiLoader(AbiLoader):
    def __init__(self, file_name: str):
        self.file_name = file_name

    def load_abi(self) -> List[Any]:
        with open(self.file_name) as f:
            return json.load(f)
