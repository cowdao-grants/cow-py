import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--with-slow", action="store_true", default=False, help="run slow tests"
    )
    parser.addoption(
        "--integration",
        action="store_true",
        default=False,
        help="run integration tests",
    )


def pytest_configure(config):
    config.addinivalue_line("markers", "slow: mark test as slow to run")
    config.addinivalue_line("markers", "integration: mark test as integration")


def pytest_collection_modifyitems(config, items):
    run_slow = config.getoption("--with-slow")
    run_integration = config.getoption("--integration")

    skip_slow = pytest.mark.skip(reason="need --with-slow option to run")
    skip_integration = pytest.mark.skip(reason="need --integration option to run")

    for item in items:
        if "slow" in item.keywords and not run_slow:
            item.add_marker(skip_slow)
        if "integration" in item.keywords and not run_integration:
            item.add_marker(skip_integration)
