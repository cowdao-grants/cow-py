from unittest.mock import patch
import pytest
from cow_py.app_data.app_data_doc import AppDataDoc
from .mocks import (
    APP_DATA_2,
    APP_DATA_DOC,
    APP_DATA_DOC_CUSTOM_VALUES,
    CID,
    CID_2,
    CID_LEGACY,
    HTTP_STATUS_INTERNAL_ERROR,
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
    app_data_doc = AppDataDoc(APP_DATA_DOC_CUSTOM_VALUES)
    assert app_data_doc.app_data_doc
    assert app_data_doc.app_data_doc.get("metadata") == APP_DATA_DOC_CUSTOM_VALUES.get(
        "metadata"
    )
    assert app_data_doc.app_data_doc.get("appCode") == APP_DATA_DOC_CUSTOM_VALUES.get(
        "appCode"
    )
    assert app_data_doc.app_data_doc.get(
        "environment"
    ) == APP_DATA_DOC_CUSTOM_VALUES.get("environment")


def test_upload_to_ipfs_legacy_without_ipfs_config():
    with pytest.raises(Exception):
        with patch("pinatapy.PinataPy.pin_json_to_ipfs") as mock_pin:
            mock_pin.return_value = {
                "status": HTTP_STATUS_INTERNAL_ERROR,
                "reason": "missing ipfs config",
                "text": "missing ipfs config",
            }
            APP_DATA_DOC.upload_to_ipfs_legacy({})


def test_upload_to_ipfs_legacy_wrong_credentials():
    with pytest.raises(Exception):
        with patch("pinatapy.PinataPy.pin_json_to_ipfs") as mock_pin:
            mock_pin.return_value = {
                "status": HTTP_STATUS_INTERNAL_ERROR,
                "reason": "wrong credentials",
                "text": "wrong credentials",
            }
            APP_DATA_DOC.upload_to_ipfs_legacy(
                {
                    "pinata_api_key": PINATA_API_KEY,
                    "pinata_api_secret": PINATA_API_SECRET,
                }
            )


def test_upload_to_ipfs_legacy():
    with patch("pinatapy.PinataPy.pin_json_to_ipfs") as mock_pin:
        mock_pin.return_value = {"IpfsHash": IPFS_HASH}
        upload_result = APP_DATA_DOC.upload_to_ipfs_legacy(
            {"pinata_api_key": PINATA_API_KEY, "pinata_api_secret": PINATA_API_SECRET}
        )
    assert upload_result == {
        "appData": IPFS_HASH_DIGEST,
        "cid": IPFS_HASH,
    }
    assert mock_pin.call_count == 1


def test_app_data_doc_to_cid():
    cid_1 = APP_DATA_DOC.to_cid()
    assert cid_1 == CID.app_data_cid

    cid_2 = APP_DATA_2.to_cid()
    assert cid_2 == CID_2.app_data_cid


def test_app_data_to_cid_legacy():
    cid = APP_DATA_DOC.to_cid_legacy()
    assert cid == CID_LEGACY.app_data_cid
