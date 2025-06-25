from dataclasses import asdict
import json

from typing import Awaitable, Callable, Dict, Optional, List, Tuple
from eth_typing import HexStr
from hexbytes import HexBytes
from web3 import Web3
from pymerkle import InmemoryTree as MerkleTree


from cowdao_cowpy.common.chains import Chain
from cowdao_cowpy.composable.utils import (
    convert_composable_cow_tradable_order_to_order_type,
    getComposableCoW,
)
from cowdao_cowpy.contracts.order import Order
from cowdao_cowpy.codegen.__generated__.ComposableCow import (
    IConditionalOrder_ConditionalOrderParams,
)

from .conditional_order import ConditionalOrder
from .types import ProofLocation, ProofWithParams, ConditionalOrderParams


class Multiplexer:
    order_type_registry: Dict[str, type] = {}

    def __init__(
        self,
        orders: Optional[Dict[str, ConditionalOrder]] = None,
        root: Optional[str] = None,
        location: ProofLocation = ProofLocation.PRIVATE,
    ):
        self.location = location
        self.orders: Dict[str, ConditionalOrder] = orders or {}
        self.tree: Optional[MerkleTree] = None
        self.ctx: Optional[str] = None

        if orders is not None and len(orders) == 0:
            raise ValueError("orders must have non-zero length")

        if (orders is not None and not root) or (orders is None and root):
            raise ValueError("orders cannot have undefined root")

        for order in self.orders.values():
            if order.order_type not in self.order_type_registry:
                raise ValueError(f"Unknown order type: {order.order_type}")

        if orders:
            self.tree = self.get_or_generate_tree()
            if self.root != root:
                raise ValueError("root mismatch")

    def add(self, order: ConditionalOrder):
        order.assert_is_valid()
        self.orders[order.id] = order
        self.reset()

    def remove(self, id: str):
        del self.orders[id]
        self.reset()

    def update(self, id: str, updater: Callable):
        order = updater(self.orders[id], self.ctx)
        del self.orders[id]
        self.orders[order.id] = order
        self.reset()

    def get_by_id(self, id: str) -> ConditionalOrder:
        return self.orders[id]

    def get_by_index(self, i: int) -> ConditionalOrder:
        return self.orders[list(self.orders.keys())[i]]

    @property
    def order_ids(self) -> List[str]:
        return list(self.orders.keys())

    def get_or_generate_tree(self) -> MerkleTree:
        if self.tree is None:
            self.tree = MerkleTree(hash_type="keccak_256")
            for order in self.orders.values():
                print(order.serialize().encode())
                self.tree.append_entry(order.serialize().encode())
        return self.tree

    @property
    def root(self) -> str:
        tree = self.get_or_generate_tree()
        root = tree.root
        if root is None:
            raise ValueError("Merkle tree root is None")
        return Web3.to_hex(root.digest)

    def get_proofs(self, filter: Optional[Callable] = None) -> List[ProofWithParams]:
        tree = self.get_or_generate_tree()
        proofs = []
        for i, order in enumerate(self.orders.values()):
            if filter is None or filter(order):
                params = ConditionalOrderParams(
                    handler=order.handler,
                    salt=order.salt,
                    static_input=order.encode_static_input(),
                )
                proofs.append(
                    ProofWithParams(proof=tree.prove_inclusion(i + 1), params=params)
                )
        return proofs

    def encode_to_abi(self, filter: Optional[Callable] = None) -> str:
        proofs = self.get_proofs(filter)
        return Web3.to_hex(Web3.keccak(text=str(proofs)))

    def encode_to_json(self, filter: Optional[Callable] = None) -> str:
        proofs = self.get_proofs(filter)
        list_to_dump = [
            {**asdict(proof.params), "path": [Web3.to_hex(p) for p in proof.proof.path]}
            for proof in proofs
        ]
        return json.dumps(list_to_dump)

    @classmethod
    def from_json(cls, s: str) -> "Multiplexer":
        data = json.loads(s)
        orders = {}
        for order_id, order_data in data["orders"].items():
            order_type = order_data.pop("orderType")
            if order_type not in cls.order_type_registry:
                raise ValueError(f"Unknown order type: {order_type}")
            order_class = cls.order_type_registry[order_type]
            orders[order_id] = order_class.from_data_dict(order_data)
        return cls(orders, data["root"], ProofLocation(data["location"]))

    def to_json(self) -> str:
        data = {
            "root": str(self.root),
            "location": self.location.value,
            "orders": {
                order_id: {
                    "orderType": order.order_type,
                    "salt": order.salt,
                    **order.data.to_dict(),
                }
                for order_id, order in self.orders.items()
            },
        }
        return json.dumps(data)

    async def prepare_proof_struct(
        self,
        location: ProofLocation = None,
        filter: Callable = None,
        uploader: Callable = None,
    ) -> tuple[int, HexBytes]:
        location = location or self.location

        async def get_data() -> str:
            if location == ProofLocation.PRIVATE:
                return "0x"
            elif location == ProofLocation.EMITTED:
                return self.encode_to_abi(filter)
            elif location in [
                ProofLocation.SWARM,
                ProofLocation.WAKU,
                ProofLocation.IPFS,
            ]:
                if not uploader:
                    raise ValueError("Must provide an uploader function")
                try:
                    return await uploader(self.encode_to_json(filter))
                except Exception as e:
                    raise ValueError(
                        f"Error uploading to decentralized storage {location}: {e}"
                    )
            else:
                raise ValueError("Unsupported location")

        data = await get_data()
        try:
            Web3.to_bytes(hexstr=HexStr(data))
            self.location = location
            return (
                location.value,
                HexBytes(data),
            )
        except Exception as e:
            raise ValueError(f"Data returned by uploader is invalid: {e}")

    @staticmethod
    async def poll(
        owner: HexStr,
        p: ProofWithParams,
        chain: Chain,
        off_chain_input_fn: Optional[
            Callable[[HexStr, ConditionalOrderParams], Awaitable[str]]
        ] = None,
    ) -> Tuple[Order, HexStr]:
        composable_cow = getComposableCoW(chain)
        off_chain_input = (
            await off_chain_input_fn(owner, p.params) if off_chain_input_fn else "0x"
        )
        (
            tradable_order,
            signature,
        ) = await composable_cow.get_tradeable_order_with_signature(
            owner,
            IConditionalOrder_ConditionalOrderParams(
                staticInput=HexBytes(p.params.static_input),
                handler=p.params.handler,
                salt=HexBytes(p.params.salt),
            ),
            HexBytes(off_chain_input),
            [HexBytes(path) for path in p.proof.path],
        )
        return (
            convert_composable_cow_tradable_order_to_order_type(tradable_order),
            Web3.to_hex(signature),
        )

    def dump_proofs(self, filter: Callable = None) -> str:
        return self.encode_to_json(filter)

    def dump_proofs_and_params(self, filter: Callable = None) -> List[ProofWithParams]:
        return self.get_proofs(filter)

    def reset(self):
        self.tree = None

    @classmethod
    def register_order_type(cls, order_type: str, conditional_order_class: type):
        cls.order_type_registry[order_type] = conditional_order_class

    @classmethod
    def reset_order_type_registry(cls):
        cls.order_type_registry = {}
