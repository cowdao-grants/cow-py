import pytest
from web3 import Web3
from cow_py.composable.order_types.twap import (
    Twap,
    TwapData,
    DurationType,
    StartTimeValue,
    TWAP_ADDRESS,
)


@pytest.fixture
def sample_twap_data():
    return TwapData(
        sell_token=Web3.to_checksum_address(
            "0x1111111111111111111111111111111111111111"
        ),
        buy_token=Web3.to_checksum_address(
            "0x2222222222222222222222222222222222222222"
        ),
        receiver=Web3.to_checksum_address("0x3333333333333333333333333333333333333333"),
        sell_amount=1000000000000000000,  # 1 ETH
        buy_amount=1000000000,  # 1 USDC
        start_time={"startType": StartTimeValue.AT_MINING_TIME.value},
        number_of_parts=10,
        time_between_parts=3600,
        duration_of_part={"durationType": DurationType.AUTO.value},
        app_data="0x0000000000000000000000000000000000000000000000000000000000000000",
    )


def test_twap_initialization(sample_twap_data):
    twap = Twap(TWAP_ADDRESS, sample_twap_data)

    assert twap.handler == TWAP_ADDRESS
    assert twap.data == sample_twap_data
    assert twap.is_single_order is True
    assert twap.order_type == "twap"


def test_twap_invalid_handler(sample_twap_data):
    with pytest.raises(ValueError, match="InvalidHandler"):
        Twap("0x1234567890123456789012345678901234567890", sample_twap_data)


def test_twap_is_valid(sample_twap_data):
    twap = Twap(TWAP_ADDRESS, sample_twap_data)
    result = twap.is_valid()

    assert result["is_valid"] is True


def test_twap_invalid_same_token(sample_twap_data):
    sample_twap_data.buy_token = sample_twap_data.sell_token
    twap = Twap(TWAP_ADDRESS, sample_twap_data)
    result = twap.is_valid()

    assert result["is_valid"] is False
    assert result["reason"] == "InvalidSameToken"


def test_twap_invalid_sell_amount(sample_twap_data):
    sample_twap_data.sell_amount = 0
    twap = Twap(TWAP_ADDRESS, sample_twap_data)
    result = twap.is_valid()

    assert result["is_valid"] is False
    assert result["reason"] == "InvalidSellAmount"


def test_twap_serialize(sample_twap_data):
    twap = Twap(TWAP_ADDRESS, sample_twap_data)
    serialized = twap.serialize()

    assert isinstance(serialized, str)
    assert serialized.startswith("0x")


def test_twap_encode_static_input(sample_twap_data):
    twap = Twap(TWAP_ADDRESS, sample_twap_data)
    encoded = twap.encode_static_input()

    assert isinstance(encoded, str)
    assert encoded.startswith("0x")


def test_twap_to_string(sample_twap_data):
    twap = Twap(TWAP_ADDRESS, sample_twap_data)
    string_repr = twap.to_string()

    assert isinstance(string_repr, str)
    assert "twap" in string_repr


def test_twap_transform_data_to_struct(sample_twap_data):
    twap = Twap(TWAP_ADDRESS, sample_twap_data)
    struct = twap.transform_data_to_struct(sample_twap_data)

    assert "sell_token" in struct.__dict__
    assert "buy_token" in struct.__dict__
    assert "part_sell_amount" in struct.__dict__
    assert "min_part_limit" in struct.__dict__
    assert "t0" in struct.__dict__
    assert "n" in struct.__dict__
    assert "t" in struct.__dict__
    assert "span" in struct.__dict__


def test_twap_transform_struct_to_data(sample_twap_data):
    twap = Twap(TWAP_ADDRESS, sample_twap_data)
    struct = twap.transform_data_to_struct(sample_twap_data)
    data = twap.transform_struct_to_data(struct)

    assert isinstance(data, TwapData)
    assert data.sell_token == struct.sell_token
    assert data.buy_token == struct.buy_token
    assert data.sell_amount == struct.part_sell_amount * struct.n
    assert data.buy_amount == struct.min_part_limit * struct.n
    assert data.start_time["startType"] == StartTimeValue.AT_MINING_TIME.value
    assert data.number_of_parts == struct.n
    assert data.time_between_parts == struct.t
    assert data.duration_of_part["durationType"] == DurationType.AUTO.value
