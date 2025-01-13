from enum import Enum

from cowdao_cowpy.common.config import SupportedChainId


class Chain(Enum):
    """
    Supported chains and their respective `chainId` for the SDK.
    """

    MAINNET = (SupportedChainId.MAINNET, "ethereum", "https://etherscan.io")
    SEPOLIA = (SupportedChainId.SEPOLIA, "sepolia", "https://sepolia.etherscan.io")
    GNOSIS = (SupportedChainId.GNOSIS_CHAIN, "gnosis", "https://gnosisscan.io")
    ARBITRUM_ONE = (
        SupportedChainId.ARBITRUM_ONE,
        "arbitrum_one",
        "https://arbiscan.io",
    )
    BASE = (SupportedChainId.BASE, "base", "https://basescan.org/")

    def __init__(
        self, id: SupportedChainId, network_name: str, explorer_url: str
    ) -> None:
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
    def chain_id(self) -> SupportedChainId:
        return self.id


SUPPORTED_CHAINS = {chain for chain in Chain}
