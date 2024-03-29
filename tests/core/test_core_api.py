import pytest
from cow_py.common import constants, cow_error, chains, config


@pytest.mark.parametrize("module", [constants, cow_error, chains, config])
def test_module_existence(module):
    assert module is not None
