import pytest
from cow_py.app_data.appDataHex import AppDataHex
from .mocks import APP_DATA_HEX, CID, APP_DATA_HEX_LEGACY, CID_LEGACY


@pytest.mark.asyncio
async def test_app_data_hex_to_cid_happy_path():
    decoded_app_data_hex = await APP_DATA_HEX.to_cid()
    assert decoded_app_data_hex.app_data_cid == CID.app_data_cid


@pytest.mark.asyncio
async def test_app_data_hex_to_cid_invalid_hash():
    app_data_hex = AppDataHex("invalidHash")
    with pytest.raises(Exception):
        await app_data_hex("invalidHash")


@pytest.mark.asyncio
async def test_app_data_hex_to_cid_legacy_happy_path():
    decoded_app_data_hex = await APP_DATA_HEX_LEGACY.to_cid_legacy()
    assert decoded_app_data_hex.app_data_cid == CID_LEGACY.app_data_cid


@pytest.mark.asyncio
async def test_app_data_hex_to_cid_legacy_invalid_hash():
    app_data_hex = AppDataHex("invalidHash")
    with pytest.raises(Exception):
        await app_data_hex.to_cid_legacy()
