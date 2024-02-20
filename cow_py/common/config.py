from enum import Enum


class IPFSConfig(Enum):
    READ_URI = "https://gnosis.mypinata.cloud/ipfs"
    WRITE_URI = "https://api.pinata.cloud"
    # TODO: ensure pinata api key is somewhere?
