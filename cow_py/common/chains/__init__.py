from enum import Enum


class Chain(Enum):
    """
    Supported chains and their respective `chainId` for the SDK.
    """

    MAINNET = 1
    GNOSIS = 100
    SEPOLIA = 11155111

    def __init__(self, id) -> None:
        self.id = id


SUPPORTED_CHAINS = {Chain.MAINNET, Chain.GNOSIS, Chain.SEPOLIA}

CHAIN_NAMES = {
    Chain.MAINNET: "ethereum",
    Chain.GNOSIS: "gnosis",
    Chain.SEPOLIA: "sepolia",
}

CHAIN_SCANNER_MAP = {
    Chain.MAINNET: "https://etherscan.io",
    Chain.GNOSIS: "https://gnosisscan.io",
    Chain.SEPOLIA: "https://sepolia.etherscan.io/",
}
