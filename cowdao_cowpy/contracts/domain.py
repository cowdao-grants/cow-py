from dataclasses import asdict, dataclass
from typing import Optional

from cowdao_cowpy.common.chains import Chain


@dataclass
class TypedDataDomain:
    name: str
    version: str
    chainId: int
    verifyingContract: str
    salt: Optional[str] = None

    def to_dict(self):
        base_dict = asdict(self)
        if "salt" in base_dict and base_dict["salt"] is None:
            del base_dict["salt"]
        return base_dict


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
        chainId=chain.chain_id.value,
        verifyingContract=verifying_contract,
    )
