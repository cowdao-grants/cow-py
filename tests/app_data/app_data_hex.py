import httpx
import pytest
from unittest.mock import patch
from cowdao_cowpy.app_data.consts import MetaDataError
from cowdao_cowpy.app_data.app_data_hex import AppDataHex
from .mocks import (
    APP_DATA_HEX,
    CID,
    HTTP_STATUS_INTERNAL_ERROR,
)


def test_app_data_hex_to_cid():
    decoded_app_data_cid = APP_DATA_HEX.to_cid()
    assert decoded_app_data_cid == CID.app_data_cid


def test_app_data_hex_to_cid_invalid_hash():
    app_data_hex = AppDataHex("invalidHash")
    with pytest.raises(Exception):
        app_data_hex.to_cid()


@pytest.mark.asyncio
async def test_fetch_doc_from_app_data_hex_invalid_hash():
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_get.return_value = httpx.Response(HTTP_STATUS_INTERNAL_ERROR)

        app_data_hex = AppDataHex("invalidHash")

        with pytest.raises(MetaDataError):
            await app_data_hex.to_doc()
