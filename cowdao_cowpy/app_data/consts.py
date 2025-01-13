import os

DEFAULT_IPFS_READ_URI = os.getenv("IPFS_READ_URI", "https://cloudflare-ipfs.com/ipfs")

LATEST_APP_DATA_VERSION = "1.1.0"
DEFAULT_APP_CODE = "CoW Swap"
DEFAULT_APP_DATA_DOC = {
    "appCode": DEFAULT_APP_CODE,
    "metadata": {},
    "version": LATEST_APP_DATA_VERSION,
}


class MetaDataError(Exception):
    pass
