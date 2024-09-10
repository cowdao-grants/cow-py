import pytest
from web3 import Web3
from cow_py.composable.multiplexer import Multiplexer
from cow_py.composable.conditional_order import ConditionalOrder
from cow_py.composable.types import ProofLocation


class TestConditionalOrder(ConditionalOrder):
    def __init__(self, handler, salt, data):
        super().__init__(handler, salt, data)

    @property
    def is_single_order(self) -> bool:
        return True

    @property
    def order_type(self) -> str:
        return "test"

    def is_valid(self) -> dict:
        return {"isValid": True}

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


@pytest.fixture
def sample_order():
    handler = Web3.to_checksum_address("0x1234567890123456789012345678901234567890")
    salt = Web3.to_hex(Web3.keccak(text="test"))
    data = {"key": "value"}
    return TestConditionalOrder(handler, salt, data)


def test_multiplexer_initialization():
    chain_id = 1
    multiplexer = Multiplexer(chain_id)

    assert multiplexer.chain_id == chain_id
    assert multiplexer.location == ProofLocation.PRIVATE
    assert len(multiplexer.orders) == 0


def test_multiplexer_add_order(sample_order):
    multiplexer = Multiplexer(1)
    multiplexer.add(sample_order)

    assert len(multiplexer.orders) == 1
    assert multiplexer.get_by_id(sample_order.id) == sample_order


def test_multiplexer_remove_order(sample_order):
    multiplexer = Multiplexer(1)
    multiplexer.add(sample_order)
    multiplexer.remove(sample_order.id)

    assert len(multiplexer.orders) == 0


def test_multiplexer_update_order(sample_order):
    multiplexer = Multiplexer(1)
    multiplexer.add(sample_order)

    def updater(order, ctx):
        order.data["updated"] = True
        return order

    multiplexer.update(sample_order.id, updater)

    updated_order = multiplexer.get_by_id(sample_order.id)
    assert updated_order.data["updated"] is True


def test_multiplexer_get_by_index(sample_order):
    multiplexer = Multiplexer(1)
    multiplexer.add(sample_order)

    assert multiplexer.get_by_index(0) == sample_order


def test_multiplexer_order_ids(sample_order):
    multiplexer = Multiplexer(1)
    multiplexer.add(sample_order)

    assert multiplexer.order_ids == [sample_order.id]


def test_multiplexer_root():
    multiplexer = Multiplexer(1)
    root = multiplexer.root

    assert isinstance(root, str)
    assert root.startswith("0x")


@pytest.mark.asyncio
async def test_multiplexer_prepare_proof_struct():
    multiplexer = Multiplexer(1)
    proof_struct = await multiplexer.prepare_proof_struct()

    assert "location" in proof_struct
    assert "data" in proof_struct


def test_multiplexer_dump_proofs():
    multiplexer = Multiplexer(1)
    proofs = multiplexer.dump_proofs()

    assert isinstance(proofs, str)


def test_multiplexer_dump_proofs_and_params():
    multiplexer = Multiplexer(1)
    proofs_and_params = multiplexer.dump_proofs_and_params()

    assert isinstance(proofs_and_params, list)


def test_multiplexer_register_order_type():
    Multiplexer.register_order_type("test", TestConditionalOrder)

    assert "test" in Multiplexer.order_type_registry
    assert Multiplexer.order_type_registry["test"] == TestConditionalOrder


def test_multiplexer_reset_order_type_registry():
    Multiplexer.register_order_type("test", TestConditionalOrder)
    Multiplexer.reset_order_type_registry()

    assert len(Multiplexer.order_type_registry) == 0
