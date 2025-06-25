from hexbytes import HexBytes
from cowdao_cowpy.common.chains import Chain
from cowdao_cowpy.codegen.components import (
    BaseMixin,
    BaseContract,
    FileAbiLoader,
    ContractFactory,
    get_abi_file,
)


class MilkmanMixin(BaseMixin):
    async def domain_separator(self) -> HexBytes:
        return await self.call_contract_method("DOMAIN_SEPARATOR")

    async def cancel_swap(
        self,
        amount_in: int,
        from_token: str,
        to_token: str,
        to: str,
        price_checker: str,
        price_checker_data: HexBytes,
    ) -> None:
        return await self.call_contract_method(
            "cancelSwap",
            amount_in,
            from_token,
            to_token,
            to,
            price_checker,
            price_checker_data,
        )

    async def initialize(self, from_token: str, _swap_hash: HexBytes) -> None:
        return await self.call_contract_method("initialize", from_token, _swap_hash)

    async def is_valid_signature(
        self, order_digest: HexBytes, encoded_order: HexBytes
    ) -> HexBytes:
        return await self.call_contract_method(
            "isValidSignature", order_digest, encoded_order
        )

    async def request_swap_exact_tokens_for_tokens(
        self,
        amount_in: int,
        from_token: str,
        to_token: str,
        to: str,
        price_checker: str,
        price_checker_data: HexBytes,
    ) -> None:
        return await self.call_contract_method(
            "requestSwapExactTokensForTokens",
            amount_in,
            from_token,
            to_token,
            to,
            price_checker,
            price_checker_data,
        )

    async def swap_hash(self) -> HexBytes:
        return await self.call_contract_method("swapHash")


class Milkman(BaseContract, MilkmanMixin):
    def __init__(self, chain: Chain = Chain.MAINNET, address: str = ""):
        abi_loader = FileAbiLoader(get_abi_file("Milkman"))
        contract = ContractFactory.create("Milkman", chain, address, abi_loader)
        super(Milkman, self).__init__(address, chain, abi=contract.ABI)
