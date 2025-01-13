from typing import Dict, Tuple, Type

from cowdao_cowpy.codegen.components.abi_loader import AbiLoader
from cowdao_cowpy.codegen.components.base_contract import BaseContract
from cowdao_cowpy.common.chains import Chain


class ContractFactory:
    _contract_classes: Dict[Tuple[str, Chain], Type[BaseContract]] = {}

    @classmethod
    def get_contract_class(
        cls, contract_name: str, chain: Chain, abi_loader: AbiLoader
    ) -> Type[BaseContract]:
        """
        Retrieves the contract class for a given contract name and chain, creating it if it doesn't exist.

        :param contract_name: The name of the contract
        :param chain: The chain the contract is deployed on
        :return: The contract class for the given contract name and chain
        """
        key = (contract_name, chain)
        if key not in cls._contract_classes:
            abi = abi_loader.load_abi()
            cls._contract_classes[key] = type(
                f"{contract_name}", (BaseContract,), {"ABI": abi}
            )
        return cls._contract_classes[key]

    @classmethod
    def create(
        cls, contract_name: str, chain: Chain, address: str, abi_loader: AbiLoader
    ) -> BaseContract:
        """
        Creates an instance of the contract class for a given contract identifier (name or address) and chain.

        :param chain: The chain the contract is deployed on
        :param contract_identifier: The name or address of the contract on the specified chain, optional
        :param address_override: address with which to instantiate the contract, optional. We do this because some
                                 pool contracts only have a MockPool contract whose ABI we'd like to use
        :return: An instance of the contract class for the given contract identifier and chain
        """
        contract_class = cls.get_contract_class(contract_name, chain, abi_loader)
        return contract_class(address, chain)
