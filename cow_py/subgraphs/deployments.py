from cow_py.common.chains import Chain
from dataclasses import dataclass
from enum import Enum


class SubgraphEnvironment(Enum):
    PRODUCTION = "production"
    STAGING = "staging"


SUBGRAPH_BASE_URL = "https://api.thegraph.com/subgraphs/name/cowprotocol"


def build_subgraph_url(chain: Chain, env: SubgraphEnvironment) -> str:
    base_url = SUBGRAPH_BASE_URL

    network_suffix = "" if chain == Chain.MAINNET else "-gc"
    env_suffix = "-" + env.value if env == SubgraphEnvironment.STAGING else ""

    if chain == Chain.SEPOLIA:
        raise ValueError(f"Unsupported chain: {chain}")

    return f"{base_url}/cow{network_suffix}{env_suffix}"


@dataclass
class SubgraphConfig:
    chain: Chain

    @property
    def production(self) -> str:
        return build_subgraph_url(self.chain, SubgraphEnvironment.PRODUCTION)

    @property
    def staging(self) -> str:
        return build_subgraph_url(self.chain, SubgraphEnvironment.STAGING)
