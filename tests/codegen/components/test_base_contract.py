import pytest
from unittest.mock import patch, Mock
from cow_py.codegen.components.base_contract import (
    BaseContract,
    Chain,
)


@patch("cow_py.codegen.components.base_contract.ContractLoader")
def test_base_contract_singleton(mock_loader):
    address = "0x123"
    chain = Chain.MAINNET
    contract1 = BaseContract(address, chain)
    contract2 = BaseContract(address, chain)
    assert (
        contract1 is contract2
    ), "BaseContract should return the same instance for the same address and chain"


class MockWithoutAttributes(Mock):
    # By default Mock objects allow access to any attribute, even if it doesn't exist.
    # on the Base Contract class, we want to raise an AttributeError if the attribute doesn't exist.
    def __getattr__(self, name: str):
        if name == "balanceOf" or name == "nonExistentMethod":
            raise AttributeError()
        return super().__getattr__(name)


@pytest.fixture
def contract_with_abi():
    abi = [
        {"type": "function", "name": "balanceOf"},
        {"type": "event", "name": "Transfer"},
    ]
    with patch("cow_py.codegen.components.base_contract.ContractLoader") as mock_loader:
        mock_contract = MockWithoutAttributes()
        mock_contract.abi = abi
        mock_contract.functions = Mock(
            balanceOf=Mock(return_value=Mock(call=Mock(return_value="1000"))),
        )

        mock_loader.return_value.get_web3_contract.return_value = mock_contract
        contract = BaseContract("0x456", Chain.MAINNET, abi)
    return contract


def test_base_contract_function_exists_in_abi(contract_with_abi):
    assert contract_with_abi._function_exists_in_abi("balanceOf")
    assert not contract_with_abi._function_exists_in_abi("transfer")


def test_base_contract_event_exists_in_abi(contract_with_abi):
    assert contract_with_abi._event_exists_in_abi("Transfer")
    assert not contract_with_abi._event_exists_in_abi("Approval")


def test_base_contract_getattr(contract_with_abi):
    assert contract_with_abi.balanceOf() == "1000"
    with pytest.raises(AttributeError):
        _ = contract_with_abi.nonExistentMethod
