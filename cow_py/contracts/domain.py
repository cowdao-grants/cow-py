from dataclasses import dataclass
from typing import Optional

from cow_py.common.chains import Chain


@dataclass
class TypedDataDomain:
    name: str
    version: str
    chainId: int
    verifyingContract: str
    salt: Optional[str] = None


def domain(chain: Chain, verifying_contract: str) -> TypedDataDomain:
    """
    Return the Gnosis Protocol v2 domain used for signing.

    :param chain: The EIP-155 chain ID.
    :param verifying_contract: The address of the contract that will verify the signature.
    :return: An EIP-712 compatible typed domain data.
    """
    return TypedDataDomain(
        name="Gnosis Protocol",
        version="v2",
        chainId=chain.chain_id,
        verifyingContract=verifying_contract,
    )
