import unittest
from unittest.mock import MagicMock, patch
from cow_py.codegen.components.contract_factory import ContractFactory, BaseContract
from cow_py.common.chains import Chain


class TestContractFactory(unittest.TestCase):
    def setUp(self):
        self.contract_name = "MockContract"
        self.chain = Chain.MAINNET
        self.abi_loader = MagicMock()
        self.abi_loader.load_abi = MagicMock(
            return_value=[{"type": "function", "name": "mockFunction"}]
        )
        self.address = "0xe91D153E0b41518A2Ce8Dd3D7944Fa863463a97d"

    def test_contract_factory_get_contract_class(self):
        with patch.dict(
            "cow_py.codegen.components.contract_factory.ContractFactory._contract_classes",
            clear=True,
        ):
            first_class = ContractFactory.get_contract_class(
                self.contract_name, self.chain, self.abi_loader
            )
            second_class = ContractFactory.get_contract_class(
                self.contract_name, self.chain, self.abi_loader
            )

            self.abi_loader.load_abi.assert_called_once()
            self.assertEqual(first_class, second_class)

    def test_contract_factory_create(self):
        with patch.dict(
            "cow_py.codegen.components.contract_factory.ContractFactory._contract_classes",
            clear=True,
        ):
            contract_instance = ContractFactory.create(
                self.contract_name, self.chain, self.address, self.abi_loader
            )

            self.assertIsInstance(contract_instance, BaseContract)
            self.assertEqual(contract_instance.address, self.address)
