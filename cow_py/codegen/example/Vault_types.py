from typing import List, Tuple, Any
from hexbytes import HexBytes
from cow_py.common.chains import Chain
from dataclasses import dataclass
from enum import Enum
from cow_py.codegen.components import (
    BaseMixin,
    BaseContract,
    FileAbiLoader,
    ContractFactory,
)


# TODO: Enums must be fixed before using them. They currently only use placeholder values.
class SwapKind(Enum):
    VALUE_1 = 1
    VALUE_2 = 2


class PoolSpecialization(Enum):
    VALUE_1 = 1
    VALUE_2 = 2


@dataclass
class FundManagement:
    sender: str
    fromInternalBalance: bool
    recipient: str
    toInternalBalance: bool


@dataclass
class ExitPoolRequest:
    assets: List[str]
    minAmountsOut: List[int]
    userData: HexBytes
    toInternalBalance: bool


@dataclass
class JoinPoolRequest:
    assets: List[str]
    maxAmountsIn: List[int]
    userData: HexBytes
    fromInternalBalance: bool


@dataclass
class SingleSwap:
    poolId: HexBytes
    kind: SwapKind
    assetIn: str
    assetOut: str
    amount: int
    userData: HexBytes


class VaultMixin(BaseMixin):
    def weth(self) -> str:
        return self.call_contract_method("WETH")

    def batch_swap(
        self,
        kind: SwapKind,
        swaps: List[Any],
        assets: List[str],
        funds: FundManagement,
        limits: List[int],
        deadline: int,
    ) -> List[int]:
        return self.call_contract_method(
            "batchSwap",
            kind,
            swaps,
            assets,
            (
                funds.sender,
                funds.fromInternalBalance,
                funds.recipient,
                funds.toInternalBalance,
            ),
            limits,
            deadline,
        )

    def deregister_tokens(self, pool_id: HexBytes, tokens: List[str]) -> None:
        return self.call_contract_method("deregisterTokens", pool_id, tokens)

    def exit_pool(
        self, pool_id: HexBytes, sender: str, recipient: str, request: ExitPoolRequest
    ) -> None:
        return self.call_contract_method(
            "exitPool",
            pool_id,
            sender,
            recipient,
            (
                request.assets,
                request.minAmountsOut,
                request.userData,
                request.toInternalBalance,
            ),
        )

    def flash_loan(
        self, recipient: str, tokens: List[str], amounts: List[int], user_data: HexBytes
    ) -> None:
        return self.call_contract_method(
            "flashLoan", recipient, tokens, amounts, user_data
        )

    def get_action_id(self, selector: HexBytes) -> HexBytes:
        return self.call_contract_method("getActionId", selector)

    def get_authorizer(self) -> str:
        return self.call_contract_method("getAuthorizer")

    def get_domain_separator(self) -> HexBytes:
        return self.call_contract_method("getDomainSeparator")

    def get_internal_balance(self, user: str, tokens: List[str]) -> List[int]:
        return self.call_contract_method("getInternalBalance", user, tokens)

    def get_next_nonce(self, user: str) -> int:
        return self.call_contract_method("getNextNonce", user)

    def get_paused_state(self) -> Tuple[bool, int, int]:
        return self.call_contract_method("getPausedState")

    def get_pool(self, pool_id: HexBytes) -> Tuple[str, PoolSpecialization]:
        return self.call_contract_method("getPool", pool_id)

    def get_pool_token_info(
        self, pool_id: HexBytes, token: str
    ) -> Tuple[int, int, int, str]:
        return self.call_contract_method("getPoolTokenInfo", pool_id, token)

    def get_pool_tokens(self, pool_id: HexBytes) -> Tuple[List[str], List[int], int]:
        return self.call_contract_method("getPoolTokens", pool_id)

    def get_protocol_fees_collector(self) -> str:
        return self.call_contract_method("getProtocolFeesCollector")

    def has_approved_relayer(self, user: str, relayer: str) -> bool:
        return self.call_contract_method("hasApprovedRelayer", user, relayer)

    def join_pool(
        self, pool_id: HexBytes, sender: str, recipient: str, request: JoinPoolRequest
    ) -> None:
        return self.call_contract_method(
            "joinPool",
            pool_id,
            sender,
            recipient,
            (
                request.assets,
                request.maxAmountsIn,
                request.userData,
                request.fromInternalBalance,
            ),
        )

    def manage_pool_balance(self, ops: List[Any]) -> None:
        return self.call_contract_method("managePoolBalance", ops)

    def manage_user_balance(self, ops: List[Any]) -> None:
        return self.call_contract_method("manageUserBalance", ops)

    def query_batch_swap(
        self, kind: SwapKind, swaps: List[Any], assets: List[str], funds: FundManagement
    ) -> List[int]:
        return self.call_contract_method(
            "queryBatchSwap",
            kind,
            swaps,
            assets,
            (
                funds.sender,
                funds.fromInternalBalance,
                funds.recipient,
                funds.toInternalBalance,
            ),
        )

    def register_pool(self, specialization: PoolSpecialization) -> HexBytes:
        return self.call_contract_method("registerPool", specialization)

    def register_tokens(
        self, pool_id: HexBytes, tokens: List[str], asset_managers: List[str]
    ) -> None:
        return self.call_contract_method(
            "registerTokens", pool_id, tokens, asset_managers
        )

    def set_authorizer(self, new_authorizer: str) -> None:
        return self.call_contract_method("setAuthorizer", new_authorizer)

    def set_paused(self, paused: bool) -> None:
        return self.call_contract_method("setPaused", paused)

    def set_relayer_approval(self, sender: str, relayer: str, approved: bool) -> None:
        return self.call_contract_method(
            "setRelayerApproval", sender, relayer, approved
        )

    def swap(
        self, single_swap: SingleSwap, funds: FundManagement, limit: int, deadline: int
    ) -> int:
        return self.call_contract_method(
            "swap",
            (
                single_swap.poolId,
                single_swap.kind,
                single_swap.assetIn,
                single_swap.assetOut,
                single_swap.amount,
                single_swap.userData,
            ),
            (
                funds.sender,
                funds.fromInternalBalance,
                funds.recipient,
                funds.toInternalBalance,
            ),
            limit,
            deadline,
        )


class Vault(BaseContract, VaultMixin):
    def __init__(self, chain: Chain = Chain.MAINNET, address: str = ""):
        abi_loader = FileAbiLoader("example/VaultABI.json")
        contract = ContractFactory.create("Vault", chain, address, abi_loader)
        super(Vault, self).__init__(address, chain, abi=contract.ABI)
