from cow_py.common.chains import CHAIN_SCANNER_MAP, Chain


def get_explorer_link(chain: Chain, tx_hash: str) -> str:
    """Return the scan link for the provided transaction hash."""
    return f"{CHAIN_SCANNER_MAP[chain]}/tx/{tx_hash}"
