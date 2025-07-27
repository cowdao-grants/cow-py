import os
from cowdao_cowpy import __version__

DEFAULT_IPFS_READ_URI = os.getenv("IPFS_READ_URI", "https://cloudflare-ipfs.com/ipfs")

LATEST_APP_DATA_VERSION = "1.3.0"
DEFAULT_APP_CODE = "cowdao_cowpy"
DEFAULT_GRAFFITI = "🥩📢🌀🐮 'MÖØ'"
DEFAULT_HOOKS_VERSION = "0.1.0"
DEFAULT_APP_DATA_DOC = {
    "appCode": DEFAULT_APP_CODE,
    "metadata": {
        "hooks": {
            "version": DEFAULT_HOOKS_VERSION,
        },
        "utm": {
            "utmSource": "cowmunity",
            "utmMedium": f"cow-py@{__version__}",
            "utmCampaign": "developer-cohort",
            "utmContent": DEFAULT_GRAFFITI,
            "utmTerm": "python",
        },
    },
    "version": LATEST_APP_DATA_VERSION,
}


class MetaDataError(Exception):
    pass
