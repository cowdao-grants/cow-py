from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional


class SupportedChainId(Enum):
    MAINNET = 1
    GNOSIS_CHAIN = 100
    SEPOLIA = 11155111
    ARBITRUM_ONE = 42161
    BASE = 8453


class CowEnv(Enum):
    PROD = "prod"
    STAGING = "staging"


ApiBaseUrls = Dict[SupportedChainId, str]


@dataclass
class ApiContext:
    chain_id: SupportedChainId
    env: CowEnv
    base_urls: Optional[ApiBaseUrls] = None
    max_tries: Optional[int] = 5


# Define the list of available environments.
ENVS_LIST = [CowEnv.PROD, CowEnv.STAGING]

# Define the default CoW Protocol API context.
DEFAULT_COW_API_CONTEXT = ApiContext(env=CowEnv.PROD, chain_id=SupportedChainId.MAINNET)


class IPFSConfig(Enum):
    READ_URI = "https://gnosis.mypinata.cloud/ipfs"
    WRITE_URI = "https://api.pinata.cloud"
    # TODO: ensure pinata api key is somewhere?
