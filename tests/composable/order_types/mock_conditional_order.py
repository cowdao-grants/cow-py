from dataclasses import dataclass
from typing import Optional, Dict, Any
from eth_typing import HexStr

from cow_py.composable.conditional_order import ConditionalOrder
from cow_py.composable.types import (
    IsValidResult,
    PollParams,
    PollResultError,
)
from cow_py.contracts.order import Order
from cow_py.composable.utils import encode_params


@dataclass
class TestConditionalOrderParams:
    handler: str
    data: str = "0x"
    salt: Optional[str] = None
    is_single_order: bool = True


DEFAULT_ORDER_PARAMS = TestConditionalOrderParams(
    handler="0x910d00a310f7Dc5B29FE73458F47f519be547D3d",
    salt="0x9379a0bf532ff9a66ffde940f94b1a025d6f18803054c1aef52dc94b15255bbe",
    data="0x",
    is_single_order=True,
)


class TestConditionalOrder(ConditionalOrder[str, str]):
    def __init__(self, params: TestConditionalOrderParams):
        super().__init__(
            handler=HexStr(params.handler),
            data=params.data,
            salt=HexStr(params.salt) if params.salt else None,
        )
        self._is_single_order = params.is_single_order

    @property
    def is_single_order(self) -> bool:
        return self._is_single_order

    @property
    def order_type(self) -> str:
        return "TEST"

    def encode_static_input(self) -> HexStr:
        return HexStr(self.static_input)

    def test_encode_static_input(self) -> HexStr:
        return self.encode_static_input_helper(["uint256"], self.static_input)

    def transform_struct_to_data(self, params: str) -> str:
        return params

    def transform_data_to_struct(self, params: str) -> str:
        return params

    async def poll_validate(self, params: PollParams) -> Optional[PollResultError]:
        return None

    async def handle_poll_failed_already_present(
        self, order_uid: str, order: Order, params: PollParams
    ) -> Optional[PollResultError]:
        return None

    def is_valid(self) -> IsValidResult:
        return IsValidResult(is_valid=True)

    def serialize(self) -> HexStr:
        return encode_params(self.leaf)

    def to_string(self, token_formatter=None) -> str:
        raise NotImplementedError("Method not implemented.")


def create_test_conditional_order(
    params: Optional[Dict[str, Any]] = None
) -> TestConditionalOrder:
    """Factory function to create test conditional orders"""
    if params is None:
        params = {}

    merged_params = TestConditionalOrderParams(
        handler=params.get("handler", DEFAULT_ORDER_PARAMS.handler),
        salt=params.get("salt", DEFAULT_ORDER_PARAMS.salt),
        data=params.get("data", DEFAULT_ORDER_PARAMS.data),
        is_single_order=params.get(
            "is_single_order", DEFAULT_ORDER_PARAMS.is_single_order
        ),
    )

    return TestConditionalOrder(merged_params)
