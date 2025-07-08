from abc import ABC

from web3.contract.async_contract import AsyncContract


class BaseMixin(ABC):
    web3_contract: AsyncContract

    def _get_method(self, method_name):
        """
        Get a contract method by name.

        :param method_name: The name of the contract method to get.
        :return: The contract method.
        """
        return getattr(self.web3_contract.functions, method_name)

    async def call_contract_method(self, method_name, *args):
        """
        Generic method to call a contract function.

        :param method_name: The name of the contract method to call.
        :param args: Arguments to pass to the contract method.
        :return: The result of the contract method call.
        """
        method = self._get_method(method_name)
        return await method(*args).call()

    def build_tx_data(self, method_name: str, *args) -> str:
        """
        Generate encoded function call data without transaction parameters.

        :param method_name: The name of the contract method to call.
        :param args: Arguments to pass to the contract method.
        :return: Hex string of the encoded function call data.
        """
        method = self._get_method(method_name)
        return method(*args).build_transaction()
