from dataclasses import dataclass
from enum import Enum

from cowdao_cowpy.common.chains import Chain


class SubgraphEnvironment(Enum):
    PRODUCTION = "production"
    STAGING = "staging"


NETWORK_SUBGRAPH_IDS_MAP = {
    Chain.MAINNET: "https://api.studio.thegraph.com/query/49707/cow-subgraph-mainnet/version/latest",
    Chain.SEPOLIA: "https://api.studio.thegraph.com/query/49707/cow-subgraph-sepolia/version/latest",
    Chain.GNOSIS: "https://api.studio.thegraph.com/query/49707/cow-subgraph-gnosis/version/latest",
    Chain.ARBITRUM_ONE: "https://api.studio.thegraph.com/query/49707/cow-subgraph-arb/version/latest",
    Chain.BASE: "https://api.studio.thegraph.com/query/49707/cow-subgraph-base/version/latest",
}


def build_subgraph_url(
    chain: Chain = Chain.MAINNET,
    env: SubgraphEnvironment = SubgraphEnvironment.PRODUCTION,
    subgraph_api_key: str = None,
) -> str:
    base_url = NETWORK_SUBGRAPH_IDS_MAP[chain]

    if env == SubgraphEnvironment.STAGING:
        raise NotImplementedError("Staging subgraph URLs are not yet implemented")

    if "{SUBGRAPH_API_KEY}" in base_url and not subgraph_api_key:
        raise ValueError("Subgraph API key is required for this subgraph")

    url = base_url.format(SUBGRAPH_API_KEY=subgraph_api_key)

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
