from eth_utils.conversions import to_hex
from eth_utils.crypto import keccak
from eth_utils.currency import to_wei

from cowdao_cowpy.common.config import SupportedChainId
from cowdao_cowpy.contracts.domain import TypedDataDomain
from cowdao_cowpy.contracts.order import Order


def fill_bytes(count, byte):
    return to_hex(bytearray([byte] * count))


def fill_distinct_bytes(count, start):
    return to_hex(bytearray([(start + i) % 256 for i in range(count)]))


def fill_uint(bits, byte):
    return int(fill_bytes(bits // 8, byte), 16)


def ceil_div(p, q):
    return (p + q - 1) // q


ORDER_KIND_SELL = "SELL"

SAMPLE_ORDER = Order(
    **{
        "sell_token": fill_bytes(20, 0x01),
        "buy_token": fill_bytes(20, 0x02),
        "receiver": fill_bytes(20, 0x03),
        "sell_amount": to_wei("42", "ether"),
        "buy_amount": to_wei("13.37", "ether"),
        "valid_to": 0xFFFFFFFF,
        "app_data": keccak(text="")[0:20],
        "fee_amount": to_wei("1.0", "ether"),
        "kind": ORDER_KIND_SELL,
        "partially_fillable": False,
    }
)

SAMPLE_DOMAIN = TypedDataDomain(
    name="Gnosis Protocol",
    version="v2",
    chainId=SupportedChainId.MAINNET.value,
    verifyingContract="0x9008D19f58AAbD9eD0D60971565AA8510560ab41",
)
