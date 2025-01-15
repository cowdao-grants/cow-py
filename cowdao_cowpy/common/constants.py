from enum import Enum
from typing import Dict

from cowdao_cowpy.common.config import SupportedChainId

from .chains import Chain

"""
This module contains constants and functions related to the CoW Protocol. It provides mappings of 
the main CoW contract addresses to CoW's supported networks.
"""


class CowContractAddress(Enum):
    VAULT_RELAYER = "0xC92E8bdf79f0507f65a392b0ab4667716BFE0110"
    COMPOSABLE_COW = "0xfdaFc9d1902f4e0b84f65F49f244b32b31013b74"
    SETTLEMENT_CONTRACT = "0x9008D19f58AAbD9eD0D60971565AA8510560ab41"
    EXTENSIBLE_FALLBACK_HANDLER = "0x2f55e8b20D0B9FEFA187AA7d00B6Cbe563605bF5"


def map_address_to_supported_networks(address) -> Dict[SupportedChainId, str]:
    """
    Maps a given address to all supported networks.

    :param address: The address to be mapped.
    :return: A dictionary mapping the address to each supported chain.
    """
    return {chain.chain_id: address for chain in Chain}


COW_PROTOCOL_SETTLEMENT_CONTRACT_CHAIN_ADDRESS_MAP = map_address_to_supported_networks(
    CowContractAddress.SETTLEMENT_CONTRACT
)
COW_PROTOCOL_VAULT_RELAYER_CHAIN_ADDRESS_MAP = map_address_to_supported_networks(
    CowContractAddress.VAULT_RELAYER
)
EXTENSIBLE_FALLBACK_HANDLER_CONTRACT_CHAIN_ADDRESS_MAP = (
    map_address_to_supported_networks(CowContractAddress.EXTENSIBLE_FALLBACK_HANDLER)
)
COMPOSABLE_COW_CONTRACT_CHAIN_ADDRESS_MAP = map_address_to_supported_networks(
    CowContractAddress.COMPOSABLE_COW
)

ZERO_APP_DATA = "0x0000000000000000000000000000000000000000000000000000000000000000"
