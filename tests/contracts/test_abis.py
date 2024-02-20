import pytest
from cow_py.contracts import abis


@pytest.mark.parametrize(
    "variable", [item for item in dir(abis) if not item.startswith("__")]
)
def test_all_variables_are_abis(variable):
    # TODO: verify that they're all valid ABIs
    assert vars(abis)[variable] is not None
