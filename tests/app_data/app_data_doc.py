from unittest.mock import patch
import pytest
from cow_py.app_data.app_data_doc import AppDataDoc
from .mocks import (
    APP_DATA_2,
    APP_DATA_DOC,
    APP_DATA_DOC_CUSTOM_VALUES,
    APP_DATA_HEX,
    APP_DATA_HEX_2,
    APP_DATA_STRING,
    APP_DATA_STRING_2,
    CID,
    CID_2,
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


def test_app_data_doc_to_string():
    string_1 = APP_DATA_DOC.to_string()
    assert string_1 == APP_DATA_STRING

    string_2 = APP_DATA_2.to_string()
    assert string_2 == APP_DATA_STRING_2


def test_app_data_doc_to_hex():
    hex_1 = APP_DATA_DOC.to_hex()
    assert hex_1 == APP_DATA_HEX.app_data_hex

    hex_2 = APP_DATA_2.to_hex()
    assert hex_2 == APP_DATA_HEX_2.app_data_hex


def test_app_data_doc_to_cid():
    cid_1 = APP_DATA_DOC.to_cid()
    assert cid_1 == CID.app_data_cid

    cid_2 = APP_DATA_2.to_cid()
    assert cid_2 == CID_2.app_data_cid
