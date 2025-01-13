from typing import List, Tuple
from hexbytes import HexBytes
from cowdao_cowpy.common.chains import Chain
from dataclasses import dataclass
from cowdao_cowpy.codegen.components import (
    BaseMixin,
    BaseContract,
    FileAbiLoader,
    ContractFactory,
    get_abi_file,
)


@dataclass
class IConditionalOrder_ConditionalOrderParams:
    handler: str
    salt: HexBytes
    staticInput: HexBytes


@dataclass
class ComposableCoW_Proof:
    location: int
    data: HexBytes


@dataclass
class GPv2Order_Data:
    sellToken: str
    buyToken: str
    receiver: str
    sellAmount: int
    buyAmount: int
    validTo: int
    appData: HexBytes
    feeAmount: int
    kind: HexBytes
    partiallyFillable: bool
    sellTokenBalance: HexBytes
    buyTokenBalance: HexBytes


class ComposableCowMixin(BaseMixin):
    def cabinet(self, str_arg_0: str, hexbytes_arg_0: HexBytes) -> HexBytes:
        return self.call_contract_method("cabinet", str_arg_0, hexbytes_arg_0)

    def create(
        self, params: IConditionalOrder_ConditionalOrderParams, dispatch: bool
    ) -> None:
        return self.call_contract_method(
            "create", (params.handler, params.salt, params.staticInput), dispatch
        )

    def create_with_context(
        self,
        params: IConditionalOrder_ConditionalOrderParams,
        factory: str,
        data: HexBytes,
        dispatch: bool,
    ) -> None:
        return self.call_contract_method(
            "createWithContext",
            (params.handler, params.salt, params.staticInput),
            factory,
            data,
            dispatch,
        )

    def domain_separator(self) -> HexBytes:
        return self.call_contract_method("domainSeparator")

    def get_tradeable_order_with_signature(
        self,
        owner: str,
        params: IConditionalOrder_ConditionalOrderParams,
        offchain_input: HexBytes,
        proof: List[HexBytes],
    ) -> Tuple[GPv2Order_Data, HexBytes]:
        return self.call_contract_method(
            "getTradeableOrderWithSignature",
            owner,
            (params.handler, params.salt, params.staticInput),
            offchain_input,
            proof,
        )

    def hash(self, params: IConditionalOrder_ConditionalOrderParams) -> HexBytes:
        return self.call_contract_method(
            "hash", (params.handler, params.salt, params.staticInput)
        )

    def is_valid_safe_signature(
        self,
        safe: str,
        sender: str,
        _hash: HexBytes,
        _domain_separator: HexBytes,
        hexbytes_arg_0: HexBytes,
        encode_data: HexBytes,
        payload: HexBytes,
    ) -> HexBytes:
        return self.call_contract_method(
            "isValidSafeSignature",
            safe,
            sender,
            _hash,
            _domain_separator,
            hexbytes_arg_0,
            encode_data,
            payload,
        )

    def remove(self, single_order_hash: HexBytes) -> None:
        return self.call_contract_method("remove", single_order_hash)

    def roots(self, str_arg_0: str) -> HexBytes:
        return self.call_contract_method("roots", str_arg_0)

    def set_root(self, root: HexBytes, proof: ComposableCoW_Proof) -> None:
        return self.call_contract_method("setRoot", root, (proof.location, proof.data))

    def set_root_with_context(
        self, root: HexBytes, proof: ComposableCoW_Proof, factory: str, data: HexBytes
    ) -> None:
        return self.call_contract_method(
            "setRootWithContext", root, (proof.location, proof.data), factory, data
        )

    def set_swap_guard(self, swap_guard: str) -> None:
        return self.call_contract_method("setSwapGuard", swap_guard)

    def single_orders(self, str_arg_0: str, hexbytes_arg_0: HexBytes) -> bool:
        return self.call_contract_method("singleOrders", str_arg_0, hexbytes_arg_0)

    def swap_guards(self, str_arg_0: str) -> str:
        return self.call_contract_method("swapGuards", str_arg_0)


class ComposableCow(BaseContract, ComposableCowMixin):
    def __init__(self, chain: Chain = Chain.MAINNET, address: str = ""):
        abi_loader = FileAbiLoader(get_abi_file("ComposableCow"))
        contract = ContractFactory.create("ComposableCow", chain, address, abi_loader)
        super(ComposableCow, self).__init__(address, chain, abi=contract.ABI)
