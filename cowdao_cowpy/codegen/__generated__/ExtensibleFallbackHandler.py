from typing import List
from hexbytes import HexBytes
from cowdao_cowpy.common.chains import Chain
from cowdao_cowpy.codegen.components import (
    BaseMixin,
    BaseContract,
    FileAbiLoader,
    ContractFactory,
    get_abi_file,
)


class ExtensibleFallbackHandlerMixin(BaseMixin):
    async def domain_verifiers(self, str_arg_0: str, hexbytes_arg_0: HexBytes) -> str:
        return await self.call_contract_method(
            "domainVerifiers", str_arg_0, hexbytes_arg_0
        )

    async def is_valid_signature(
        self, _hash: HexBytes, signature: HexBytes
    ) -> HexBytes:
        return await self.call_contract_method("isValidSignature", _hash, signature)

    async def on_erc_1155_batch_received(
        self,
        str_arg_0: str,
        str_arg_1: str,
        int_list_arg_0: List[int],
        int_list_arg_1: List[int],
        hexbytes_arg_0: HexBytes,
    ) -> HexBytes:
        return await self.call_contract_method(
            "onERC1155BatchReceived",
            str_arg_0,
            str_arg_1,
            int_list_arg_0,
            int_list_arg_1,
            hexbytes_arg_0,
        )

    async def on_erc_1155_received(
        self,
        str_arg_0: str,
        str_arg_1: str,
        int_arg_0: int,
        int_arg_1: int,
        hexbytes_arg_0: HexBytes,
    ) -> HexBytes:
        return await self.call_contract_method(
            "onERC1155Received",
            str_arg_0,
            str_arg_1,
            int_arg_0,
            int_arg_1,
            hexbytes_arg_0,
        )

    async def on_erc_721_received(
        self, str_arg_0: str, str_arg_1: str, int_arg_0: int, hexbytes_arg_0: HexBytes
    ) -> HexBytes:
        return await self.call_contract_method(
            "onERC721Received", str_arg_0, str_arg_1, int_arg_0, hexbytes_arg_0
        )

    async def safe_interfaces(self, str_arg_0: str, hexbytes_arg_0: HexBytes) -> bool:
        return await self.call_contract_method(
            "safeInterfaces", str_arg_0, hexbytes_arg_0
        )

    async def safe_methods(self, str_arg_0: str, hexbytes_arg_0: HexBytes) -> HexBytes:
        return await self.call_contract_method("safeMethods", str_arg_0, hexbytes_arg_0)

    async def set_domain_verifier(
        self, domain_separator: HexBytes, new_verifier: str
    ) -> None:
        return await self.call_contract_method(
            "setDomainVerifier", domain_separator, new_verifier
        )

    async def set_safe_method(self, selector: HexBytes, new_method: HexBytes) -> None:
        return await self.call_contract_method("setSafeMethod", selector, new_method)

    async def set_supported_interface(
        self, interface_id: HexBytes, supported: bool
    ) -> None:
        return await self.call_contract_method(
            "setSupportedInterface", interface_id, supported
        )

    async def set_supported_interface_batch(
        self, _interface_id: HexBytes, handler_with_selectors: List[HexBytes]
    ) -> None:
        return await self.call_contract_method(
            "setSupportedInterfaceBatch", _interface_id, handler_with_selectors
        )

    async def supports_interface(self, interface_id: HexBytes) -> bool:
        return await self.call_contract_method("supportsInterface", interface_id)


class ExtensibleFallbackHandler(BaseContract, ExtensibleFallbackHandlerMixin):
    def __init__(self, chain: Chain = Chain.MAINNET, address: str = ""):
        abi_loader = FileAbiLoader(get_abi_file("ExtensibleFallbackHandler"))
        contract = ContractFactory.create(
            "ExtensibleFallbackHandler", chain, address, abi_loader
        )
        super(ExtensibleFallbackHandler, self).__init__(
            address, chain, abi=contract.ABI
        )
