import pytest
from cow_py.common.chains import Chain
from cow_py.subgraphs.deployments import (
    build_subgraph_url,
    SubgraphConfig,
    SubgraphEnvironment,
    SUBGRAPH_BASE_URL,
)


def test_build_subgraph_url():
    assert (
        build_subgraph_url(Chain.MAINNET, SubgraphEnvironment.PRODUCTION)
        == f"{SUBGRAPH_BASE_URL}/cow"
    )
    assert (
        build_subgraph_url(Chain.MAINNET, SubgraphEnvironment.STAGING)
        == f"{SUBGRAPH_BASE_URL}/cow-staging"
    )
    assert (
        build_subgraph_url(Chain.GNOSIS, SubgraphEnvironment.PRODUCTION)
        == f"{SUBGRAPH_BASE_URL}/cow-gc"
    )
    assert (
        build_subgraph_url(Chain.GNOSIS, SubgraphEnvironment.STAGING)
        == f"{SUBGRAPH_BASE_URL}/cow-gc-staging"
    )

    with pytest.raises(ValueError):
        build_subgraph_url(Chain.SEPOLIA, SubgraphEnvironment.PRODUCTION)


def test_subgraph_config():
    mainnet_config = SubgraphConfig(Chain.MAINNET)
    assert mainnet_config.production == f"{SUBGRAPH_BASE_URL}/cow"
    assert mainnet_config.staging == f"{SUBGRAPH_BASE_URL}/cow-staging"

    gnosis_chain_config = SubgraphConfig(Chain.GNOSIS)
    assert gnosis_chain_config.production == f"{SUBGRAPH_BASE_URL}/cow-gc"
    assert gnosis_chain_config.staging == f"{SUBGRAPH_BASE_URL}/cow-gc-staging"

    with pytest.raises(ValueError):
        SubgraphConfig(Chain.SEPOLIA).production
