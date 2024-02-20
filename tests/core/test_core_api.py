import pytest
from cow_py.common import constants, cow_error, abis, chains, config, utils


@pytest.mark.parametrize("module", [constants, cow_error, abis, chains, config, utils])
def test_module_existence(module):
    assert module is not None
