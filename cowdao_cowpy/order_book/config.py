from typing import Dict, Literal, Type

from cowdao_cowpy.common.api.api_base import APIConfig
from cowdao_cowpy.common.config import SupportedChainId

# Define the Envs type
Envs = Literal["prod", "staging"]


class ProdAPIConfig(APIConfig):
    config_map = {
        SupportedChainId.MAINNET: "https://api.cow.fi/mainnet",
        SupportedChainId.SEPOLIA: "https://api.cow.fi/sepolia",
        SupportedChainId.GNOSIS_CHAIN: "https://api.cow.fi/xdai",
        SupportedChainId.ARBITRUM_ONE: "https://api.cow.fi/arbitrum_one",
        SupportedChainId.BASE: "https://api.cow.fi/base",
    }

    def __init__(self, chain_id: SupportedChainId, base_context=None):
        super().__init__(chain_id, base_context)
        self.env = "prod"  # Store the environment

    def with_env(self, env: Envs) -> APIConfig:
        """Switch to a different environment configuration."""
        if env == self.env:
            return self
        return OrderBookAPIConfigFactory.get_config(env, self.chain_id)


class StagingAPIConfig(APIConfig):
    config_map = {
        SupportedChainId.MAINNET: "https://barn.api.cow.fi/mainnet",
        SupportedChainId.SEPOLIA: "https://barn.api.cow.fi/sepolia",
        SupportedChainId.GNOSIS_CHAIN: "https://barn.api.cow.fi/xdai",
        SupportedChainId.ARBITRUM_ONE: "https://barn.api.cow.fi/arbitrum_one",
        SupportedChainId.BASE: "https://barn.api.cow.fi/base",
    }

    def __init__(self, chain_id: SupportedChainId, base_context=None):
        super().__init__(chain_id, base_context)
        self.env = "staging"  # Store the environment

    def with_env(self, env: Envs) -> APIConfig:
        """Switch to a different environment configuration."""
        if env == self.env:
            return self
        return OrderBookAPIConfigFactory.get_config(env, self.chain_id)


class OrderBookAPIConfigFactory:
    config_classes: Dict[Envs, Type[APIConfig]] = {
        "prod": ProdAPIConfig,
        "staging": StagingAPIConfig,
    }

    @staticmethod
    def get_config(env: Envs, chain_id: SupportedChainId) -> APIConfig:
        """Get a config instance for the specified environment and chain."""
        config_class = OrderBookAPIConfigFactory.config_classes.get(env)

        if config_class:
            return config_class(chain_id)
        else:
            raise ValueError(f"Unknown environment: {env}")
