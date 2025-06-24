import pytest

from cowdao_cowpy.common.chains import Chain
from cow_py.composable.multiplexer import Multiplexer
from cow_py.composable.types import ProofLocation
from cow_py.composable.order_types.twap import Twap
from cow_py.composable.utils import getComposableCoW

from .order_types.mock_twap_data import generate_random_twap_data


class TestMultiplexerConstruction:
    def setup_method(self):
        # Register TWAP handler before each test
        Multiplexer.register_order_type("twap", Twap)

    def teardown_method(self):
        Multiplexer.reset_order_type_registry()

    def test_can_create_new_multiplexer(self):
        m = Multiplexer()
        assert m is not None

    def test_orders_cannot_have_zero_length(self):
        with pytest.raises(ValueError, match="orders must have non-zero length"):
            Multiplexer({})

    def test_cannot_have_undefined_root_for_orders(self):
        twap = Twap.from_data(generate_random_twap_data())
        with pytest.raises(ValueError, match="orders cannot have undefined root"):
            Multiplexer({twap.id: twap})

    def test_order_types_must_be_registered(self):
        Multiplexer.reset_order_type_registry()
        twap = Twap.from_data(generate_random_twap_data())

        with pytest.raises(ValueError, match=f"Unknown order type: {twap.order_type}"):
            Multiplexer({twap.id: twap}, "0x1234")

    def test_orders_must_have_valid_root_supplied(self):
        twap = Twap.from_data(generate_random_twap_data())
        with pytest.raises(ValueError, match="root mismatch"):
            Multiplexer({twap.id: twap}, "0x1234")


class TestMultiplexerCRUD:
    def setup_method(self):
        Multiplexer.register_order_type("twap", Twap)
        self.m = Multiplexer()

    def test_crud_operations(self):
        # Add a TWAP order
        twap = Twap.from_data(generate_random_twap_data())
        self.m.add(twap)

        # Get order by id
        order = self.m.get_by_id(twap.id)
        assert order is not None
        assert order == twap

        # Get order by index
        order2 = self.m.get_by_index(0)
        assert order2 is not None
        assert order2 == twap

        # Add another TWAP order
        twap2 = Twap.from_data(generate_random_twap_data())
        self.m.add(twap2)

        # Confirm two orders exist
        assert len(self.m.order_ids) == 2

        # Store root for comparison
        root = self.m.root

        # Remove first order
        self.m.remove(twap.id)

        # Confirm one order remains
        assert len(self.m.order_ids) == 1

        # Update second order
        def updater(old_order, ctx):
            return twap

        self.m.update(twap2.id, updater)

        # Confirm one order exists
        assert len(self.m.order_ids) == 1

        # Confirm root has changed
        assert self.m.root != root

        # Get updated order
        order3 = self.m.get_by_id(twap.id)
        assert order3 is not None
        assert order3 == twap

    def test_cannot_add_invalid_orders(self):
        # Create invalid TWAP with negative time between parts
        invalid_data = generate_random_twap_data()
        invalid_data.time_between_parts = -1
        invalid_twap = Twap.from_data(invalid_data)

        with pytest.raises(ValueError, match="Invalid order: InvalidFrequency"):
            self.m.add(invalid_twap)


class TestMultiplexerSerialization:
    def setup_method(self):
        Multiplexer.register_order_type("twap", Twap)
        self.m = Multiplexer()

    def test_can_serialize_to_json(self):
        # Add a TWAP order
        twap = Twap.from_data(generate_random_twap_data())
        self.m.add(twap)

        # Serialize
        serialized = self.m.to_json()
        assert serialized is not None

        # Serialize again to check for side effects
        serialized2 = self.m.to_json()
        assert serialized2 is not None
        assert serialized2 == serialized

    def test_enforce_registered_order_types_on_deserialization(self):
        # Add a TWAP order and serialize
        twap = Twap.from_data(generate_random_twap_data())
        self.m.add(twap)
        serialized = self.m.to_json()

        # Reset registry and attempt deserialization
        Multiplexer.reset_order_type_registry()

        with pytest.raises(ValueError, match="Unknown order type: twap"):
            Multiplexer.from_json(serialized)

    def test_can_serialize_and_deserialize(self):
        # Add multiple random TWAP orders
        for _ in range(10):
            self.m.add(Twap.from_data(generate_random_twap_data()))

        # Get random order for comparison
        import random

        index = random.randint(0, 9)
        order_before = self.m.get_by_index(index)
        order_id = order_before.id

        # Serialize
        serialized = self.m.to_json()

        # Deserialize
        m2 = Multiplexer.from_json(serialized)

        # Compare orders
        order_after = m2.get_by_id(order_id)
        assert order_before.id == order_after.id


class TestMultiplexerProofs:
    def setup_method(self):
        Multiplexer.register_order_type("twap", Twap)
        self.m = Multiplexer()

    @pytest.mark.asyncio
    async def test_prepare_proof_struct_basic(self):
        # Add multiple TWAP orders
        for _ in range(10):
            self.m.add(Twap.from_data(generate_random_twap_data()))

        proof_struct = await self.m.prepare_proof_struct()

        # Verify struct can be used with ComposableCow contract
        composable_cow = getComposableCoW(Chain.MAINNET)
        try:
            composable_cow.build_tx_data("setRoot", self.m.root, proof_struct)
        except Exception as e:
            pytest.fail(f"Failed to encode function data: {e}")

    @pytest.mark.asyncio
    async def test_prepare_proof_struct_emitted(self):
        twap = Twap.from_data(generate_random_twap_data())
        self.m.add(twap)

        proof_struct = await self.m.prepare_proof_struct(ProofLocation.EMITTED)

        composable_cow = getComposableCoW(Chain.MAINNET)
        try:
            composable_cow.build_tx_data("setRoot", self.m.root, proof_struct)
        except Exception as e:
            pytest.fail(f"Failed to encode function data: {e}")

    @pytest.mark.asyncio
    async def test_prepare_proof_struct_uploader(self):
        twap = Twap.from_data(generate_random_twap_data())
        self.m.add(twap)

        # Test without uploader
        with pytest.raises(ValueError, match="Must provide an uploader function"):
            await self.m.prepare_proof_struct(ProofLocation.SWARM)

        # Test with invalid uploader response
        async def bad_uploader(_data: str) -> str:
            return "baddata"

        with pytest.raises(ValueError, match="Data returned by uploader is invalid"):
            await self.m.prepare_proof_struct(
                ProofLocation.SWARM, uploader=bad_uploader
            )

        # Test with failing uploader
        async def failing_uploader(_data: str) -> str:
            raise Exception("bad")

        with pytest.raises(
            ValueError, match="Error uploading to decentralized storage"
        ):
            await self.m.prepare_proof_struct(
                ProofLocation.IPFS, uploader=failing_uploader
            )
