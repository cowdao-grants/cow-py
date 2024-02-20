from typing import Dict
from .chains import Chain

BUY_ETH_ADDRESS = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"

VAULT_RELAYER = "0xC92E8bdf79f0507f65a392b0ab4667716BFE0110"
COMPOSABLE_COW = "0xfdaFc9d1902f4e0b84f65F49f244b32b31013b74"
SETTLEMENT_CONTRACT = "0x9008D19f58AAbD9eD0D60971565AA8510560ab41"
EXTENSIBLE_FALLBACK_HANDLER = "0x2f55e8b20D0B9FEFA187AA7d00B6Cbe563605bF5"


def map_address_to_supported_networks(address: str) -> Dict[Chain, str]:
    return {chain_id: address for chain_id in Chain}


""" An object containing the addresses of the CoW Protocol settlement contracts for each supported chain. """
COW_PROTOCOL_SETTLEMENT_CONTRACT_CHAIN_ADDRESS_MAP = map_address_to_supported_networks(
    SETTLEMENT_CONTRACT
)

""" An object containing the addresses of the CoW Protocol Vault relayer contracts for each supported chain. """
COW_PROTOCOL_VAULT_RELAYER_CHAIN_ADDRESS_MAP = map_address_to_supported_networks(
    VAULT_RELAYER
)

""" An object containing the addresses of the `ExtensibleFallbackHandler` contracts for each supported chain.   """
EXTENSIBLE_FALLBACK_HANDLER_CONTRACT_CHAIN_ADDRESS_MAP = (
    map_address_to_supported_networks(EXTENSIBLE_FALLBACK_HANDLER)
)

""" An object containing the addresses of the `ComposableCow` contracts for each supported chain. """
COMPOSABLE_COW_CONTRACT_CHAIN_ADDRESS_MAP = map_address_to_supported_networks(
    COMPOSABLE_COW
)
