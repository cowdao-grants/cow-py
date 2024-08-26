from unittest.mock import patch
import httpx
import pytest
from cow_py.app_data.app_data_doc import AppDataDoc
from .mocks import (
    APP_DATA_DOC_CUSTOM,
    HTTP_STATUS_INTERNAL_ERROR,
    HTTP_STATUS_OK,
    IPFS_HASH,
    IPFS_HASH_DIGEST,
    PINATA_API_KEY,
    PINATA_API_SECRET,
)


def test_init_empty_metadata():
    app_data_doc = AppDataDoc()
    assert app_data_doc.app_data_doc.get("version")
    assert app_data_doc.app_data_doc.get("metadata") == {}
    assert app_data_doc.app_data_doc.get("appCode") == "CoW Swap"
    assert app_data_doc.app_data_doc.get("environment") is None


def test_init_custom_metadata():
    app_data_doc = AppDataDoc(APP_DATA_DOC_CUSTOM)
    assert app_data_doc.app_data_doc
    assert app_data_doc.app_data_doc.get("metadata") == APP_DATA_DOC_CUSTOM.get(
        "metadata"
    )
    assert app_data_doc.app_data_doc.get("appCode") == APP_DATA_DOC_CUSTOM.get(
        "appCode"
    )
    assert app_data_doc.app_data_doc.get("environment") == APP_DATA_DOC_CUSTOM.get(
        "environment"
    )


def test_upload_to_ipfs_legacy_without_ipfs_config():
    app_data_doc = AppDataDoc()
    with pytest.raises(Exception):
        with patch("pinatapy.PinataPy.pin_json_to_ipfs") as mock_pin:
            mock_pin.return_value = {
                "status": HTTP_STATUS_INTERNAL_ERROR,
                "reason": "missing ipfs config",
                "text": "missing ipfs config",
            }
            app_data_doc.upload_to_ipfs_legacy({})


def test_upload_to_ipfs_legacy_wrong_credentials():
    app_data_doc = AppDataDoc()
    with pytest.raises(Exception):
        with patch("pinatapy.PinataPy.pin_json_to_ipfs") as mock_pin:
            mock_pin.return_value = {
                "status": HTTP_STATUS_INTERNAL_ERROR,
                "reason": "wrong credentials",
                "text": "wrong credentials",
            }
            app_data_doc.upload_to_ipfs_legacy(
                {
                    "pinata_api_key": PINATA_API_KEY,
                    "pinata_api_secret": PINATA_API_SECRET,
                }
            )


def test_upload_to_ipfs_legacy():
    app_data_doc = AppDataDoc(APP_DATA_DOC_CUSTOM)
    with patch("pinatapy.PinataPy.pin_json_to_ipfs") as mock_pin:
        mock_pin.return_value = {"IpfsHash": IPFS_HASH}
        upload_result = app_data_doc.upload_to_ipfs_legacy(
            {"pinata_api_key": PINATA_API_KEY, "pinata_api_secret": PINATA_API_SECRET}
        )
    assert upload_result == {
        "appData": IPFS_HASH_DIGEST,
        "cid": IPFS_HASH,
    }
    assert mock_pin.call_count == 1
