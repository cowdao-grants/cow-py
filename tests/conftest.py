"""
# -*- coding: utf-8 -*-
This is used to configure the pytest environment.
"""

import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--run-integration",
        action="store_true",
        default=False,
        help="run integration tests",
    )


def pytest_runtest_setup(item):
    if "integration" in item.keywords and not item.config.getoption(
        "--run-integration"
    ):
        pytest.skip("skipping integration test, use --run-integration to enable")
