from cow_py.app_data.appDataCid import AppDataCid
from cow_py.app_data.appDataHex import AppDataHex

HTTP_STATUS_OK = 200
HTTP_STATUS_INTERNAL_ERROR = 500

APP_DATA_DOC = {
    "version": "0.7.0",
    "appCode": "CoW Swap",
    "metadata": {},
}

APP_DATA_STRING = '{"appCode":"CoW Swap","metadata":{},"version":"0.7.0"}'

CID = AppDataCid("f01551b20337aa6e6c2a7a0d1eb79a35ebd88b08fc963d5f7a3fc953b7ffb2b7f5898a1df")

APP_DATA_HEX = AppDataHex(
    "0x337aa6e6c2a7a0d1eb79a35ebd88b08fc963d5f7a3fc953b7ffb2b7f5898a1df"
)

APP_DATA_DOC_CUSTOM = {
    **APP_DATA_DOC,
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

CID_2 = "f01551b208af4e8c9973577b08ac21d17d331aade86c11ebcc5124744d621ca8365ec9424"

APP_DATA_HEX_2 = "0x8af4e8c9973577b08ac21d17d331aade86c11ebcc5124744d621ca8365ec9424"

APP_DATA_STRING_LEGACY = '{"version":"0.7.0","appCode":"CowSwap","metadata":{}}'

CID_LEGACY = AppDataCid("QmSwrFbdFcryazEr361YmSwtGcN4uo4U5DKpzA4KbGxw4Q")

APP_DATA_HEX_LEGACY = AppDataHex(
    "0x447320af985c5e834321dc495545f764ad20d8397eeed2f4a2dcbee44a56b725"
)

PINATA_API_KEY = "apikey"
PINATA_API_SECRET = "apiSecret"