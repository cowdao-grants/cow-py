from eth_utils.conversions import to_hex
from eth_utils.crypto import keccak
from eth_utils.currency import to_wei

from cow_py.contracts.order import Order


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
        "sellToken": fill_bytes(20, 0x01),
        "buyToken": fill_bytes(20, 0x02),
        "receiver": fill_bytes(20, 0x03),
        "sellAmount": to_wei("42", "ether"),
        "buyAmount": to_wei("13.37", "ether"),
        "validTo": 0xFFFFFFFF,
        "appData": keccak(text="")[0:20],
        "feeAmount": to_wei("1.0", "ether"),
        "kind": ORDER_KIND_SELL,
        "partiallyFillable": False,
    }
)
