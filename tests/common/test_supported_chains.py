from cowdao_cowpy.common.chains import SUPPORTED_CHAINS, Chain
from cowdao_cowpy.common.config import SupportedChainId

EXPECTED_CHAIN_IDS = {
    "MAINNET": 1,
    "GNOSIS_CHAIN": 100,
    "SEPOLIA": 11155111,
    "ARBITRUM_ONE": 42161,
    "BASE": 8453,
    "POLYGON": 137,
    "AVALANCHE": 43114,
    "BNB": 56,
    "LINEA": 59144,
    "PLASMA": 9745,
    "INK": 57073,
}


def test_supported_chain_ids_match_expected():
    actual = {chain.name: chain.value for chain in SupportedChainId}
    assert actual == EXPECTED_CHAIN_IDS


def test_every_supported_chain_id_has_a_chain_entry():
    chain_ids = {chain.chain_id for chain in Chain}
    assert chain_ids == set(SupportedChainId)


def test_lens_is_removed():
    # api.cow.fi/lens was decommissioned; the TS SDK removed Lens in v8.0.0.
    assert "LENS" not in SupportedChainId.__members__
    assert "LENS" not in Chain.__members__


def test_supported_chains_set_matches_chain_enum():
    assert SUPPORTED_CHAINS == set(Chain)
