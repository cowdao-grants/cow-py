from dataclasses import dataclass
from enum import Enum

from cow_py.common.chains import Chain


class SubgraphEnvironment(Enum):
    PRODUCTION = "production"
    STAGING = "staging"


NETWORK_SUBGRAPH_IDS_MAP = {
    Chain.MAINNET: "https://gateway.thegraph.com/api/{SUBGRAPH_API_KEY}/subgraphs/id/8mdwJG7YCSwqfxUbhCypZvoubeZcFVpCHb4zmHhvuKTD",
    Chain.SEPOLIA: "https://api.studio.thegraph.com/query/49707/cow-subgraph-sepolia/version/latest",
    Chain.GNOSIS: "https://gateway.thegraph.com/api/{SUBGRAPH_API_KEY}/subgraphs/id/HTQcP2gLuAy235CMNE8ApN4cbzpLVjjNxtCAUfpzRubq",
    Chain.ARBITRUM: "https://gateway.thegraph.com/api/{SUBGRAPH_API_KEY}/subgraphs/id/CQ8g2uJCjdAkUSNkVbd9oqqRP2GALKu1jJCD3fyY5tdc",
}


def build_subgraph_url(
    chain: Chain = Chain.SEPOLIA,
    env: SubgraphEnvironment = SubgraphEnvironment.PRODUCTION,
    subgraph_api_key: str = "",
) -> str:
    base_url = NETWORK_SUBGRAPH_IDS_MAP[chain]

    if env == SubgraphEnvironment.STAGING:
        raise NotImplementedError("Staging subgraph URLs are not yet implemented")

    url = base_url.format(SUBGRAPH_API_KEY=subgraph_api_key)

    if "{SUBGRAPH_API_KEY}" in url:
        raise ValueError("Subgraph API key is required for this subgraph")

    return url


@dataclass
class SubgraphConfig:
    chain: Chain

    @property
    def production(self) -> str:
        return build_subgraph_url(self.chain, SubgraphEnvironment.PRODUCTION)

    @property
    def staging(self) -> str:
        return build_subgraph_url(self.chain, SubgraphEnvironment.STAGING)
