from typing import Dict

import web3

from cowdao_cowpy.common.chains import Chain

DEFAULT_PROVIDER_NETWORK_MAPPING = {
    Chain.MAINNET: "https://rpc.mevblocker.io",
    Chain.GNOSIS: "https://gnosis.publicnode.com",
    Chain.SEPOLIA: "https://ethereum-sepolia.publicnode.com",
    Chain.ARBITRUM_ONE: "https://arbitrum.llamarpc.com",
    Chain.BASE: "https://base.llamarpc.com",
}


class Web3Provider:
    """
    A singleton class that manages web3 instances for different chains.

    :ivar _instances: A dictionary to store web3 instances for each chain.
    """

    _instances: Dict[Chain, web3.AsyncWeb3] = {}

    @classmethod
    def get_instance(
        cls,
        chain=Chain.MAINNET,
        request_kwargs={},
        provider_network_mapping=DEFAULT_PROVIDER_NETWORK_MAPPING,
    ) -> web3.AsyncWeb3:
        """
        Retrieves or creates a web3 instance for the specified chain.

        :param chain: The Chain object representing the blockchain.
        :return: An AsyncWeb3 instance for the specified chain.
        """
        if chain not in cls._instances:
            cls._instances[chain] = web3.AsyncWeb3(
                web3.AsyncHTTPProvider(provider_network_mapping[chain], request_kwargs)
            )
        return cls._instances[chain]
