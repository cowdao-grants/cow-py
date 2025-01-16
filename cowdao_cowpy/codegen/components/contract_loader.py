from cowdao_cowpy.web3.provider import Web3Provider


class ContractLoaderError(Exception):
    """Raised when an error occurs in the ContractLoader class."""

    pass


class ContractLoader:
    """
    A utility class to load contract ABIs and create web3 contract instances.
    """

    def __init__(self, network):
        """
        Initializes a ContractLoader instance for a specified network.

        :param network: The network the contract loader is associated with.
        """
        self.network = network
        self._abis = {}

    def get_web3_contract(self, contract_address, abi=None):
        """
        Creates a web3 contract instance for the specified contract address and ABI.

        :param contract_address: The address of the contract.
        :param abi_file_name: The file name of the ABI, optional.
        :return: A web3 contract instance.

        Raises:
            ContractLoaderError: If an error occurs while creating the web3 contract instance.
        """
        try:
            w3 = Web3Provider.get_instance(self.network)

            return w3.eth.contract(
                address=w3.to_checksum_address(contract_address),
                abi=abi,
            )
        except Exception as e:
            raise ContractLoaderError(f"Error loading contract: {str(e)}") from e
