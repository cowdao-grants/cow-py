import httpx
import pytest
from unittest.mock import patch
from cowdao_cowpy.app_data.app_data_cid import AppDataCid
from cowdao_cowpy.app_data.consts import DEFAULT_IPFS_READ_URI
from .mocks import APP_DATA_HEX, CID, APP_DATA_HEX_2, CID_2


@pytest.mark.asyncio
async def test_fetch_doc_from_cid():
    valid_serialized_cid = "QmZZhNnqMF1gRywNKnTPuZksX7rVjQgTT3TJAZ7R6VE3b2"
    expected = {
        "appCode": "CowSwap",
        "metadata": {
            "referrer": {
                "address": "0x1f5B740436Fc5935622e92aa3b46818906F416E9",
                "version": "0.1.0",
            }
        },
        "version": "0.1.0",
    }

    with patch("httpx.AsyncClient.get") as mock_get:
        mock_get.return_value = httpx.Response(200, json=expected)

        app_data_hex = AppDataCid(valid_serialized_cid)
        app_data_document = await app_data_hex.to_doc()

    assert app_data_document == expected
    mock_get.assert_called_once_with(f"{DEFAULT_IPFS_READ_URI}/{valid_serialized_cid}")


def test_app_data_cid_to_hex():
    decoded_app_data_hex = CID.to_hex()
    assert decoded_app_data_hex == APP_DATA_HEX.app_data_hex

    decoded_app_data_hex_2 = CID_2.to_hex()
    assert decoded_app_data_hex_2 == APP_DATA_HEX_2.app_data_hex


def test_app_data_cid_to_hex_invalid_hash():
    app_data_cid = AppDataCid("invalidCid")
    with pytest.raises(Exception):
        app_data_cid.to_hex()
