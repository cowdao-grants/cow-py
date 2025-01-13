import pytest

from cowdao_cowpy.common import chains, config, constants, cow_error


@pytest.mark.parametrize("module", [constants, cow_error, chains, config])
def test_module_existence(module):
    assert module is not None
