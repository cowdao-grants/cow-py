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


class TWAPMixin(BaseMixin):
    def get_tradeable_order(
        self,
        owner: str,
        str_arg_0: str,
        ctx: HexBytes,
        static_input: HexBytes,
        hexbytes_arg_0: HexBytes,
    ) -> GPv2Order_Data:
        return self.call_contract_method(
            "getTradeableOrder", owner, str_arg_0, ctx, static_input, hexbytes_arg_0
        )

    def supports_interface(self, interface_id: HexBytes) -> bool:
        return self.call_contract_method("supportsInterface", interface_id)

    def verify(
        self,
        owner: str,
        sender: str,
        _hash: HexBytes,
        domain_separator: HexBytes,
        ctx: HexBytes,
        static_input: HexBytes,
        offchain_input: HexBytes,
        gpv_2order_data_arg_0: GPv2Order_Data,
    ) -> None:
        return self.call_contract_method(
            "verify",
            owner,
            sender,
            _hash,
            domain_separator,
            ctx,
            static_input,
            offchain_input,
            (
                gpv_2order_data_arg_0.sellToken,
                gpv_2order_data_arg_0.buyToken,
                gpv_2order_data_arg_0.receiver,
                gpv_2order_data_arg_0.sellAmount,
                gpv_2order_data_arg_0.buyAmount,
                gpv_2order_data_arg_0.validTo,
                gpv_2order_data_arg_0.appData,
                gpv_2order_data_arg_0.feeAmount,
                gpv_2order_data_arg_0.kind,
                gpv_2order_data_arg_0.partiallyFillable,
                gpv_2order_data_arg_0.sellTokenBalance,
                gpv_2order_data_arg_0.buyTokenBalance,
            ),
        )


class TWAP(BaseContract, TWAPMixin):
    def __init__(self, chain: Chain = Chain.MAINNET, address: str = ""):
        abi_loader = FileAbiLoader(get_abi_file("TWAP"))
        contract = ContractFactory.create("TWAP", chain, address, abi_loader)
        super(TWAP, self).__init__(address, chain, abi=contract.ABI)
