from typing import Dict, List, Optional, Tuple, Any, Type
from cow_py.common.chains import Chain
from cow_py.codegen.components.contract_loader import ContractLoader


class BaseContract:
    """
    A base class for contracts that implements common functionality.

    This class uses a singleton pattern to ensure that there's only one instance
    of the contract for each contract address and chain combination.

    :ivar _instances: A dictionary to store instances of the BaseContract class.
    """

    ABI: Optional[List[Any]] = None
    _instances: Dict[Tuple[Type, str, Chain], "BaseContract"] = {}

    def __new__(cls, address, chain, *args, **kwargs):
        key = (cls, address, chain)
        if key not in cls._instances:
            cls._instances[key] = super(BaseContract, cls).__new__(cls)
        return cls._instances[key]

    def __init__(self, address: str, chain: Chain, abi=None):
        """
        Initializes the BaseContract with a contract address, chain, and optionally an ABI file name.

        :param address: The address of the contract on the specified chain
        :param chain: The chain the contract is deployed on
        :param abi_file_name: The ABI file name of the contract, optional
        :param abi: The ABI of the contract, optional
        """
        if not hasattr(self, "_initialized"):  # Avoid re-initialization
            # Initialize the instance (only the first time)
            self.contract_loader = ContractLoader(chain)
            self.web3_contract = self.contract_loader.get_web3_contract(
                address, self.ABI if abi is None else abi
            )
            self._initialized = True

    @property
    def address(self) -> str:
        return self.web3_contract.address

    def _function_exists_in_abi(self, function_name):
        """
        Checks if a function exists in the ABI of the contract.

        :param function_name: The name of the function to check for
        :return: True if the function exists, False otherwise
        """
        for item in self.web3_contract.abi:
            if item.get("type") == "function" and item.get("name") == function_name:
                return True
        return False

    def _event_exists_in_abi(self, event_name):
        """
        Checks if an event exists in the ABI of the contract.

        :param event_name: The name of the event to check for
        :return: True if the event exists, False otherwise
        """
        for item in self.web3_contract.abi:
            if item.get("type") == "event" and item.get("name") == event_name:
                return True
        return False

    def __getattr__(self, name):
        """
        Makes contract functions directly accessible as attributes of the BaseContract.

        :param name: The name of the attribute being accessed
        :return: The wrapped contract function if it exists, raises AttributeError otherwise
        """
        if name == "_initialized":
            # This is needed to avoid infinite recursion
            raise AttributeError(name)

        if getattr(self.web3_contract, name, None):
            return getattr(self.web3_contract, name)

        if self._event_exists_in_abi(name):
            # TODO: ability to get event signature hash
            function = getattr(self.web3_contract.events, name)

        if self._function_exists_in_abi(name):
            function = getattr(self.web3_contract.functions, name)

            def wrapped_call(*args, **kwargs):
                return function(*args, **kwargs).call()

            return wrapped_call

        raise AttributeError(f"{self.__class__.__name__} has no attribute {name}")
