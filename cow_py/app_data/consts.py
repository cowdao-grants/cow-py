import os

DEFAULT_IPFS_READ_URI = os.getenv("IPFS_READ_URI", "https://cloudflare-ipfs.com/ipfs")
DEFAULT_IPFS_WRITE_URI = os.getenv("IPFS_WRITE_URI", "https://api.pinata.cloud")


class MetaDataError(Exception):
    pass
