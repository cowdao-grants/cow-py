"""
Tests for uploading application data to the COW server.
"""

from examples.appdata import main


def test_upload_app_data():
    """
    Test the upload of application data to the COW server.
    """
    app_data_hash = main()
    assert isinstance(app_data_hash, str)
