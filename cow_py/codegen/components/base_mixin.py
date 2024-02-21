from abc import ABC

from web3.contract.async_contract import AsyncContract


class BaseMixin(ABC):
    web3_contract: AsyncContract

    def call_contract_method(self, method_name, *args):
        """
        Generic method to call a contract function.

        :param method_name: The name of the contract method to call.
        :param args: Arguments to pass to the contract method.
        :return: The result of the contract method call.
        """
        method = getattr(self.web3_contract.functions, method_name)
        return method(*args).call()
