from typing import Dict, Literal, Type

from cow_py.common.api.api_base import APIConfig
from cow_py.common.config import SupportedChainId


class ProdAPIConfig(APIConfig):
    config_map = {
        SupportedChainId.MAINNET: "https://api.cow.fi/mainnet",
        SupportedChainId.GNOSIS_CHAIN: "https://api.cow.fi/xdai",
        SupportedChainId.SEPOLIA: "https://api.cow.fi/sepolia",
    }


class StagingAPIConfig(APIConfig):
    config_map = {
        SupportedChainId.MAINNET: "https://barn.api.cow.fi/mainnet",
        SupportedChainId.GNOSIS_CHAIN: "https://barn.api.cow.fi/xdai",
        SupportedChainId.SEPOLIA: "https://barn.api.cow.fi/sepolia",
    }


Envs = Literal["prod", "staging"]


class OrderBookAPIConfigFactory:
    config_classes: Dict[Envs, Type[APIConfig]] = {
        "prod": ProdAPIConfig,
        "staging": StagingAPIConfig,
    }

    @staticmethod
    def get_config(env: Envs, chain_id: SupportedChainId) -> APIConfig:
        config_class = OrderBookAPIConfigFactory.config_classes.get(env)

        if config_class:
            return config_class(chain_id)
        else:
            raise ValueError("Unknown environment")
