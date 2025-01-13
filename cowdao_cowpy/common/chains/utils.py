from cowdao_cowpy.common.chains import Chain


def get_explorer_link(chain: Chain, tx_hash: str) -> str:
    """Return the scan link for the provided transaction hash."""
    return f"{chain.explorer_url}/tx/{tx_hash}"
