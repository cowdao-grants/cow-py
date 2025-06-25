from typing import List, Any, Dict
from eth_typing import HexStr
from hexbytes import HexBytes
from web3 import Web3
from eth_abi.abi import encode, decode


from cowdao_cowpy.common.chains import Chain
from cowdao_cowpy.common.constants import (
    COMPOSABLE_COW_CONTRACT_CHAIN_ADDRESS_MAP,
    EXTENSIBLE_FALLBACK_HANDLER_CONTRACT_CHAIN_ADDRESS_MAP,
)
from cowdao_cowpy.codegen.__generated__.ExtensibleFallbackHandler import (
    ExtensibleFallbackHandler,
)
from cowdao_cowpy.composable.types import ConditionalOrderParams
from cowdao_cowpy.contracts.order import (
    Order,
    bytes32_to_balance_kind,
    bytes32_to_order_kind,
)
from cowdao_cowpy.codegen.__generated__.ComposableCow import (
    GPv2Order_Data,
    ComposableCow,
)


def encode_params(params: ConditionalOrderParams) -> HexStr:
    return Web3.to_hex(
        encode(
            ["(address,bytes32,bytes)"],
            [
                [
                    params.handler,
                    HexBytes(params.salt),
                    HexBytes(params.static_input),
                ]
            ],
        )
    )


def decode_params(encoded: HexStr) -> ConditionalOrderParams:
    [decoded] = decode(["(address,bytes32,bytes)"], HexBytes(encoded))
    return ConditionalOrderParams(
        handler=decoded[0],
        salt=Web3.to_hex(decoded[1]),
        static_input=Web3.to_hex(decoded[2]),
    )


def is_valid_abi(types: List[str], values: List[Any]) -> bool:
    try:
        encode(types, values)
        return True
    except Exception:
        return False


def format_epoch(epoch: int) -> str:
    from datetime import datetime

    return datetime.fromtimestamp(epoch).isoformat()


def hash_order(domain: Dict[str, Any], order: Dict[str, Any]) -> str:
    domain_separator = Web3.keccak(
        ["bytes32", "bytes32"],
        [
            Web3.keccak(["string"], ["EIP712Domain"]),
            Web3.keccak(
                ["string", "string", "uint256", "address"],
                [
                    domain["name"],
                    domain["version"],
                    domain["chainId"],
                    domain["verifyingContract"],
                ],
            ),
        ],
    )

    struct_hash = Web3.keccak(
        ["bytes32", "bytes32"],
        [
            Web3.keccak(["string"], ["Order"]),
            Web3.keccak(encode_order(order)),
        ],
    )

    return Web3.to_hex(
        Web3.keccak(
            ["string", "bytes32", "bytes32"],
            ["\x19\x01", domain_separator, struct_hash],
        )
    )


def encode_order(order: Dict[str, Any]) -> bytes:
    return encode(
        [
            "address",
            "address",
            "address",
            "uint256",
            "uint256",
            "uint32",
            "bytes32",
            "uint256",
            "string",
            "bool",
            "string",
            "string",
        ],
        [
            order["sellToken"],
            order["buyToken"],
            order["receiver"],
            order["sellAmount"],
            order["buyAmount"],
            order["validTo"],
            order["appData"],
            order["feeAmount"],
            order["kind"],
            order["partiallyFillable"],
            order["sellTokenBalance"],
            order["buyTokenBalance"],
        ],
    )


def hash_order_cancellation(domain: Dict[str, Any], order_uid: str) -> str:
    return hash_order_cancellations(domain, [order_uid])


def hash_order_cancellations(domain: Dict[str, Any], order_uids: List[str]) -> str:
    domain_separator = Web3.keccak(
        ["bytes32", "bytes32"],
        [
            Web3.keccak(["string"], ["EIP712Domain"]),
            Web3.keccak(
                ["string", "string", "uint256", "address"],
                [
                    domain["name"],
                    domain["version"],
                    domain["chainId"],
                    domain["verifyingContract"],
                ],
            ),
        ],
    )

    struct_hash = Web3.keccak(
        ["bytes32", "bytes32"],
        [
            Web3.keccak(["string"], ["OrderCancellations"]),
            Web3.keccak(encode(["bytes[]"], [order_uids])),
        ],
    )

    return Web3.to_hex(
        Web3.keccak(
            ["string", "bytes32", "bytes32"],
            ["\x19\x01", domain_separator, struct_hash],
        )
    )


def from_struct_to_order(order: Dict[str, Any]) -> Dict[str, Any]:
    return {
        **order,
        "kind": kind_to_string(order["kind"]),
        "sellTokenBalance": balance_to_string(order["sellTokenBalance"]),
        "buyTokenBalance": balance_to_string(order["buyTokenBalance"]),
    }


def balance_to_string(balance: str) -> str:
    if balance in [
        "erc20",
        "0x5a28e9363bb942b639270062aa6bb295f434bcdfc42c97267bf003f272060dc9",
    ]:
        return "erc20"
    elif balance in [
        "external",
        "0xabee3b73373acd583a130924aad6dc38cfdc44ba0555ba94ce2ff63980ea0632",
    ]:
        return "external"
    elif balance in [
        "internal",
        "0x4ac99ace14ee0a5ef932dc609df0943ab7ac16b7583634612f8dc35a4289a6ce",
    ]:
        return "internal"
    else:
        raise ValueError(f"Unknown balance type: {balance}")


def kind_to_string(kind: str) -> str:
    if kind in [
        "sell",
        "0xf3b277728b3fee749481eb3e0b3b48980dbbab78658fc419025cb16eee346775",
    ]:
        return "sell"
    elif kind in [
        "buy",
        "0x6ed88e868af0a1983e3886d5f3e95a2fafbd6c3450bc229e27342283dc429ccc",
    ]:
        return "buy"
    else:
        raise ValueError(f"Unknown kind: {kind}")


async def get_domain_verifier(safe: str, domain: HexBytes, chain: Chain) -> str:
    contract = ExtensibleFallbackHandler(
        chain=chain,
        address=EXTENSIBLE_FALLBACK_HANDLER_CONTRACT_CHAIN_ADDRESS_MAP[
            chain.chain_id
        ].value,
    )

    return contract.domain_verifiers(safe, domain)


def create_set_domain_verifier_tx(domain: str, verifier: str, chain: Chain) -> str:
    contract = ExtensibleFallbackHandler(
        chain=chain,
        address=EXTENSIBLE_FALLBACK_HANDLER_CONTRACT_CHAIN_ADDRESS_MAP[
            chain.chain_id
        ].value,
    )

    return contract.build_tx_data("setDomainVerifier", domain, verifier)


def convert_composable_cow_tradable_order_to_order_type(
    tradable_order: GPv2Order_Data,
) -> Order:
    return Order(
        kind=bytes32_to_order_kind(tradable_order.kind),
        sell_amount=str(tradable_order.sellAmount),
        buy_amount=str(tradable_order.buyAmount),
        sell_token=tradable_order.sellToken,
        buy_token=tradable_order.buyToken,
        receiver=tradable_order.receiver,
        valid_to=tradable_order.validTo,
        app_data=tradable_order.appData.hex(),
        fee_amount=str(tradable_order.feeAmount),
        partially_fillable=tradable_order.partiallyFillable,
        sell_token_balance=bytes32_to_balance_kind(tradable_order.sellTokenBalance),
        buy_token_balance=bytes32_to_balance_kind(tradable_order.buyTokenBalance),
    )


def getComposableCoW(chain: Chain) -> ComposableCow:
    return ComposableCow(
        chain, COMPOSABLE_COW_CONTRACT_CHAIN_ADDRESS_MAP[chain.chain_id].value
    )  # type: ignore
