from secrets import token_bytes
from web3 import Web3

from cow_py.composable.order_types.twap import DurationType, StartType, TwapData


def generate_random_twap_data():
    """Helper function to generate random TWAP data mimicking TypeScript implementation"""

    def random_address():
        return Web3.to_checksum_address(Web3.to_hex(token_bytes(20)))

    ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"
    ONE_ETHER = Web3.to_wei(1, "ether")  # Equivalent to parseEther('1')

    return TwapData(
        sell_token=random_address(),
        buy_token=random_address(),
        receiver=ZERO_ADDRESS,
        sell_amount=ONE_ETHER,
        buy_amount=ONE_ETHER,
        time_between_parts=60 * 60,
        number_of_parts=10,
        duration_type=DurationType.AUTO,
        start_type=StartType.AT_MINING_TIME,
        app_data=Web3.to_hex(token_bytes(32)),
    )
