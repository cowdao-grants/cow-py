from enum import Enum


class Chain(Enum):
    """
    Supported chains and their respective `chainId` for the SDK.
    """

    MAINNET = (1, "ethereum", "https://etherscan.io")
    GNOSIS = (100, "gnosis", "https://gnosisscan.io")
    SEPOLIA = (11155111, "sepolia", "https://sepolia.etherscan.io")

    def __init__(self, id: int, network_name: str, explorer_url: str) -> None:
        self.id = id
        self.network_name = network_name
        self.explorer_url = explorer_url

    @property
    def name(self) -> str:
        return self.network_name

    @property
    def explorer(self) -> str:
        return self.explorer_url

    @property
    def chain_id(self) -> int:
        return self.id


SUPPORTED_CHAINS = {chain for chain in Chain}
