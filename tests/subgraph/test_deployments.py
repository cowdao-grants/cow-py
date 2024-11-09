import pytest

from cow_py.common.chains import Chain
from cow_py.subgraph.deployments import (
    SubgraphConfig,
    SubgraphEnvironment,
    build_subgraph_url,
    NETWORK_SUBGRAPH_IDS_MAP,
)


@pytest.fixture
def api_key():
    return "test_api_key"


def test_build_subgraph_url_sepolia():
    url = build_subgraph_url(Chain.SEPOLIA)
    assert url == NETWORK_SUBGRAPH_IDS_MAP[Chain.SEPOLIA]


def test_build_subgraph_url_with_api_key(api_key):
    chains_requiring_key = [Chain.MAINNET, Chain.GNOSIS, Chain.ARBITRUM]

    for chain in chains_requiring_key:
        url = build_subgraph_url(chain=chain, subgraph_api_key=api_key)
        expected_url = NETWORK_SUBGRAPH_IDS_MAP[chain].format(SUBGRAPH_API_KEY=api_key)
        assert url == expected_url


def test_build_subgraph_url_missing_api_key():
    chains_requiring_key = [Chain.MAINNET, Chain.GNOSIS, Chain.ARBITRUM]

    for chain in chains_requiring_key:
        with pytest.raises(
            ValueError, match="Subgraph API key is required for this subgraph"
        ):
            build_subgraph_url(chain=chain)


def test_build_subgraph_url_staging_environment():
    with pytest.raises(
        NotImplementedError, match="Staging subgraph URLs are not yet implemented"
    ):
        build_subgraph_url(Chain.MAINNET, SubgraphEnvironment.STAGING, "api_key")


def test_subgraph_config_staging():
    for chain in Chain:
        config = SubgraphConfig(chain)
        with pytest.raises(
            NotImplementedError, match="Staging subgraph URLs are not yet implemented"
        ):
            config.staging


def test_network_subgraph_ids_map_completeness():
    for chain in Chain:
        assert chain in NETWORK_SUBGRAPH_IDS_MAP


def test_subgraph_urls_format():
    for chain, url in NETWORK_SUBGRAPH_IDS_MAP.items():
        assert url.startswith("https://")
        if chain != Chain.SEPOLIA:
            assert "{SUBGRAPH_API_KEY}" in url
        else:
            assert "{SUBGRAPH_API_KEY}" not in url
