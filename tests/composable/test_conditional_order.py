from typing import Any, Dict, Optional
import pytest
from web3 import Web3
from cow_py.composable.conditional_order import ConditionalOrder
from cow_py.composable.types import IsValidResult, PollParams, GPv2OrderStruct


class TestConditionalOrder(ConditionalOrder):
    def __init__(self, handler: str, salt: str, data: str):
        super().__init__(handler, salt, data)

    @property
    def is_single_order(self) -> bool:
        return True

    @property
    def order_type(self) -> str:
        return "test"

    def is_valid(self) -> IsValidResult:
        return {"is_valid": True}

    def to_string(self, token_formatter=None) -> str:
        return "TestConditionalOrder"

    def serialize(self) -> str:
        return "serialized"

    def encode_static_input(self) -> str:
        return "0x"

    def transform_struct_to_data(self, params):
        return params

    def transform_data_to_struct(self, params):
        return params

    async def poll_validate(self, params: PollParams) -> Optional[Dict[str, Any]]:
        return None

    async def handle_poll_failed_already_present(
        self, order_uid: str, order: GPv2OrderStruct, params: PollParams
    ) -> Optional[Dict[str, Any]]:
        return None


@pytest.fixture
def sample_order():
    handler = Web3.to_checksum_address("0x1234567890123456789012345678901234567890")
    salt = Web3.keccak(text="test").hex()
    data = {"key": "value"}
    return TestConditionalOrder(handler, salt, data)


def test_conditional_order_initialization(sample_order):
    assert sample_order.handler == "0x1234567890123456789012345678901234567890"
    assert len(sample_order.salt) == 66  # "0x" + 64 hex characters
    assert sample_order.data == {"key": "value"}
    assert sample_order.is_single_order is True
    assert sample_order.order_type == "test"


def test_conditional_order_invalid_handler():
    with pytest.raises(ValueError, match="Invalid handler"):
        TestConditionalOrder("0xdeadbeef", "0x" + "0" * 64, {})


def test_conditional_order_invalid_salt():
    handler = Web3.to_checksum_address("0x1234567890123456789012345678901234567890")
    with pytest.raises(ValueError, match="Invalid salt"):
        TestConditionalOrder(handler, "0xdeadbeef", {})


def test_conditional_order_id(sample_order):
    assert len(sample_order.id) == 66  # "0x" + 64 hex characters


def test_conditional_order_ctx(sample_order):
    assert sample_order.ctx == sample_order.id


def test_conditional_order_off_chain_input(sample_order):
    assert sample_order.off_chain_input == "0x"


def test_conditional_order_is_valid(sample_order):
    assert sample_order.is_valid() == {"is_valid": True}


def test_conditional_order_serialize(sample_order):
    assert sample_order.serialize() == "serialized"


def test_conditional_order_encode_static_input(sample_order):
    assert sample_order.encode_static_input() == "0x"
