"""
Tests for uploading application data to the COW server.
"""

from cowdao_cowpy.app_data.utils import DEFAULT_APP_DATA_HASH, build_all_app_codes


def test_upload_app_data():
    """
    Test the upload of application data to the COW server.
    """
    app_data_hash = build_all_app_codes()
    assert isinstance(app_data_hash, str)
    assert (
        app_data_hash == DEFAULT_APP_DATA_HASH
    ), "App data hash does not match the default value."
