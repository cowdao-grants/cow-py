import pytest

from cowdao_cowpy.common.chains import Chain
from cowdao_cowpy.subgraph.deployments import (
    SubgraphConfig,
    SubgraphEnvironment,
    build_subgraph_url,
    NETWORK_SUBGRAPH_IDS_MAP,
)


UNDEPLOYED_CHAINS = [Chain.AVALANCHE, Chain.POLYGON, Chain.BNB, Chain.LENS]


@pytest.fixture
def api_key():
    return "test_api_key"


def test_build_subgraph_url_sepolia():
    url = build_subgraph_url(Chain.SEPOLIA)
    assert url == NETWORK_SUBGRAPH_IDS_MAP[Chain.SEPOLIA]


def test_build_subgraph_url_with_api_key(api_key):
    chains_requiring_key = [Chain.MAINNET, Chain.GNOSIS, Chain.ARBITRUM_ONE]

    for chain in chains_requiring_key:
        url = build_subgraph_url(chain=chain, subgraph_api_key=api_key)
        expected_url = NETWORK_SUBGRAPH_IDS_MAP[chain].format(SUBGRAPH_API_KEY=api_key)
        assert url == expected_url


def test_build_subgraph_url_staging_environment():
    with pytest.raises(
        NotImplementedError, match="Staging subgraph URLs are not yet implemented"
    ):
        build_subgraph_url(Chain.MAINNET, SubgraphEnvironment.STAGING, "api_key")


def test_subgraph_config_staging():
    for chain in Chain:
        if chain in UNDEPLOYED_CHAINS:
            continue
        config = SubgraphConfig(chain)
        with pytest.raises(
            NotImplementedError, match="Staging subgraph URLs are not yet implemented"
        ):
            config.staging


def test_network_subgraph_ids_map_completeness():
    for chain in Chain:
        if chain in UNDEPLOYED_CHAINS:
            continue
        assert chain in NETWORK_SUBGRAPH_IDS_MAP
