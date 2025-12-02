"""
Test cases to verify that all chains specified in the OpenAPI spec are present.
"""

import pytest
from cowdao_cowpy.common.chains import Chain, SupportedChainId
import yaml
from pathlib import Path

from cowdao_cowpy.order_book.config import ProdAPIConfig, StagingAPIConfig

ALIAS_MAP = {
    "xdai": "gnosis",
}


@pytest.fixture
def open_api_spec_chains():
    spec_path = Path("openapi.yml")
    spec = yaml.safe_load(spec_path.read_text())
    return spec["servers"]


@pytest.mark.parametrize("env", ["(Prod)", "(Staging)"])
def test_all_open_api_spec_chains_in_supported_chains(open_api_spec_chains, env):
    unsupported_chains = []
    for server in open_api_spec_chains:
        if env not in server["description"]:
            continue
        url = server["url"]
        chain_name = url.split("/")[-1]
        try:
            alias_name = chain_name
            if chain_name in ALIAS_MAP:
                alias_name = ALIAS_MAP[chain_name]
            Chain[alias_name.upper()]
        except KeyError:
            unsupported_chains.append(chain_name)
    assert not unsupported_chains, f"The following {env} chains in the OpenAPI spec are not supported: {unsupported_chains}"


@pytest.mark.parametrize("orderbook_config_class", [ProdAPIConfig, StagingAPIConfig])
def test_all_supported_chain_ids_in_orderbook_config(orderbook_config_class):
    missing_chain_ids = []
    for chain in SupportedChainId:
        try:
            orderbook_config_class.config_map[chain]
        except KeyError:
            missing_chain_ids.append(chain)
    assert not missing_chain_ids, f"The following SupportedChainIds are missing in {orderbook_config_class.__name__}: {missing_chain_ids}"


def test_all_supported_chains_in_readme():
    readme_path = Path("README.md")
    readme_content = readme_path.read_text().lower()
    missing_chains = []
    for chain in Chain:
        if chain.name not in readme_content:
            missing_chains.append(chain.name)
    assert (
        not missing_chains
    ), f"The following Chains are missing in README.md: {missing_chains}"
