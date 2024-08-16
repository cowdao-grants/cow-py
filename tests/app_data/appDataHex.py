from email.policy import HTTP
import httpx
import pytest
from cow_py.app_data.appDataCid import AppDataCid
from unittest.mock import patch
from cow_py.app_data.consts import DEFAULT_IPFS_READ_URI, MetaDataError
from cow_py.app_data.appDataHex import AppDataHex
from .mocks import (
    APP_DATA_DOC_CUSTOM,
    APP_DATA_HEX,
    CID,
    APP_DATA_HEX_LEGACY,
    CID_LEGACY,
    HTTP_STATUS_INTERNAL_ERROR,
    HTTP_STATUS_OK,
)


def test_app_data_hex_to_cid():
    decoded_app_data_cid = APP_DATA_HEX.to_cid()
    assert decoded_app_data_cid == CID.app_data_cid


def test_app_data_hex_to_cid_invalid_hash():
    app_data_hex = AppDataHex("invalidHash")
    with pytest.raises(Exception):
        app_data_hex.to_cid()


def test_app_data_hex_to_cid_legacy():
    decoded_app_data_cid = APP_DATA_HEX_LEGACY.to_cid_legacy()
    assert decoded_app_data_cid == CID_LEGACY.app_data_cid


def test_app_data_hex_to_cid_legacy_invalid_hash():
    app_data_hex = AppDataHex("invalidHash")
    with pytest.raises(Exception):
        app_data_hex.to_cid_legacy()


@pytest.mark.asyncio
async def test_fetch_doc_from_app_data_hex_legacy():
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_get.return_value = httpx.Response(HTTP_STATUS_OK, json=APP_DATA_DOC_CUSTOM)
        mock_get.return_value.status_code = HTTP_STATUS_OK

        app_data_doc = await APP_DATA_HEX_LEGACY.to_doc_legacy()

        mock_get.assert_called_once_with(
            f"{DEFAULT_IPFS_READ_URI}/{CID_LEGACY.app_data_cid}"
        )
        assert app_data_doc == APP_DATA_DOC_CUSTOM


@pytest.mark.asyncio
async def test_fetch_doc_from_app_data_hex_invalid_hash():
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_get.return_value = httpx.Response(HTTP_STATUS_INTERNAL_ERROR)

        app_data_hex = AppDataHex("invalidHash")

        with pytest.raises(MetaDataError):
            await app_data_hex.to_doc()
