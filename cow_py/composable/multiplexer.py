import json

from typing import Callable, Dict, Any, Optional, List, Tuple
from web3 import Web3
from pymerkle import InmemoryTree as MerkleTree

from .conditional_order import ConditionalOrder
from .types import ProofLocation, ProofWithParams, ConditionalOrderParams


class Multiplexer:
    order_type_registry: Dict[str, type] = {}

    def __init__(
        self,
        chain_id: int,
        orders: Optional[Dict[str, ConditionalOrder]] = None,
        root: Optional[str] = None,
        location: ProofLocation = ProofLocation.PRIVATE,
    ):
        self.chain_id = chain_id
        self.location = location
        self.orders: Dict[str, ConditionalOrder] = orders or {}
        self.tree: Optional[MerkleTree] = None
        self.ctx: Optional[str] = None

        if orders:
            if len(orders) == 0:
                raise ValueError("orders must have non-zero length")
            if not root:
                raise ValueError("orders cannot have undefined root")
            for order in orders.values():
                if order.order_type not in self.order_type_registry:
                    raise ValueError(f"Unknown order type: {order.order_type}")
            self.generate_tree()
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
            self.tree = MerkleTree()
            for order in self.orders.values():
                self.tree.append(order.serialize().encode())
        return self.tree

    @property
    def root(self) -> str:
        tree = self.get_or_generate_tree()
        root = tree.root
        if root is None:
            raise ValueError("Merkle tree root is None")
        return root.digest

    def get_proofs(self, filter: Optional[Callable] = None) -> List[ProofWithParams]:
        tree = self.get_or_generate_tree()
        proofs = []
        for i, order in enumerate(self.orders.values()):
            if filter is None or filter(order):
                params = ConditionalOrderParams(
                    handler=order.handler,
                    salt=order.salt,
                    staticInput=order.encode_static_input(),
                )
                proofs.append(ProofWithParams(proof=tree.get_proof(i), params=params))
        return proofs

    def encode_to_abi(self, filter: Optional[Callable] = None) -> str:
        proofs = self.get_proofs(filter)
        return Web3.to_hex(Web3.keccak(text=str(proofs)))

    def encode_to_json(self, filter: Optional[Callable] = None) -> str:
        return str(self.get_proofs(filter))

    def from_json(cls, s: str) -> "Multiplexer":
        data = json.loads(s)
        orders = {}
        for order_id, order_data in data["orders"].items():
            order_type = order_data.pop("orderType")
            order_class = cls.order_type_registry[order_type]
            orders[order_id] = order_class(**order_data)
        return cls(
            data["chainId"], orders, data["root"], ProofLocation(data["location"])
        )

    def to_json(self) -> str:
        data = {
            "chain_id": self.chain_id,
            "root": self.root,
            "location": self.location.value,
            "orders": {
                order_id: {"order_type": order.order_type, **order.__dict__}
                for order_id, order in self.orders.items()
            },
        }
        return str(data)

    async def prepare_proof_struct(
        self,
        location: ProofLocation = None,
        filter: Callable = None,
        uploader: Callable = None,
    ) -> Dict[str, Any]:
        location = location or self.location

        async def get_data():
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
            Web3.to_bytes(hexstr=data)
            self.location = location
            return {
                "location": location.value,
                "data": data,
            }
        except Exception as e:
            raise ValueError(f"Data returned by uploader is invalid: {e}")

    @staticmethod
    async def poll(
        owner: str,
        p: ProofWithParams,
        chain_id: int,
        provider: Any,
        off_chain_input_fn: Optional[Callable] = None,
    ) -> Tuple[Any, str]:
        # Implement poll logic here
        pass

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
