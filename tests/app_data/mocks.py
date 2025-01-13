from cowdao_cowpy.app_data.app_data_cid import AppDataCid
from cowdao_cowpy.app_data.app_data_doc import AppDataDoc
from cowdao_cowpy.app_data.app_data_hex import AppDataHex

HTTP_STATUS_OK = 200
HTTP_STATUS_INTERNAL_ERROR = 500

APP_DATA_STRING = '{"appCode":"CoW Swap","metadata":{},"version":"0.7.0"}'
APP_DATA_DOC = AppDataDoc(
    {
        "version": "0.7.0",
        "appCode": "CoW Swap",
        "metadata": {},
    },
    APP_DATA_STRING,
)


CID = AppDataCid(
    "f01551b20337aa6e6c2a7a0d1eb79a35ebd88b08fc963d5f7a3fc953b7ffb2b7f5898a1df"
)

APP_DATA_HEX = AppDataHex(
    "0x337aa6e6c2a7a0d1eb79a35ebd88b08fc963d5f7a3fc953b7ffb2b7f5898a1df"
)

APP_DATA_DOC_CUSTOM_VALUES = {
    **APP_DATA_DOC.app_data_doc,
    "environment": "test",
    "metadata": {
        "referrer": {
            "address": "0x1f5B740436Fc5935622e92aa3b46818906F416E9",
            "version": "0.1.0",
        },
        "quote": {
            "slippageBips": 1,
            "version": "0.2.0",
        },
    },
}

APP_DATA_STRING_2 = '{"appCode":"CoW Swap","environment":"production","metadata":{"quote":{"slippageBips":"50","version":"0.2.0"},"orderClass":{"orderClass":"market","version":"0.1.0"}},"version":"0.6.0"}'

APP_DATA_2 = AppDataDoc(
    {
        "appCode": "CoW Swap",
        "environment": "production",
        "metadata": {
            "quote": {"slippageBips": "50", "version": "0.2.0"},
            "orderClass": {"orderClass": "market", "version": "0.1.0"},
        },
        "version": "0.6.0",
    },
    APP_DATA_STRING_2,
)


CID_2 = AppDataCid(
    "f01551b208af4e8c9973577b08ac21d17d331aade86c11ebcc5124744d621ca8365ec9424"
)

APP_DATA_HEX_2 = AppDataHex(
    "0x8af4e8c9973577b08ac21d17d331aade86c11ebcc5124744d621ca8365ec9424"
)


PINATA_API_KEY = "apikey"
PINATA_API_SECRET = "apiSecret"

IPFS_HASH = "QmU4j5Y6JM9DqQ6yxB6nMHq4GChWg1zPehs1U7nGPHABRu"
IPFS_HASH_DIGEST = "0x5511c4eac66ab272d9a6ab90e07977d00ff7375fc4dc1038a3c05b2c16ca0b74"
