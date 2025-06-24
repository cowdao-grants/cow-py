from dataclasses import asdict
import pytest
from unittest.mock import AsyncMock, Mock
from web3 import Web3
from eth_typing import HexStr


from cowdao_cowpy.common.chains import Chain
from cow_py.composable.order_types.twap import (
    Twap,
    TwapData,
    TWAP_ADDRESS,
    DurationType,
    StartType,
)
from cowdao_cowpy.contracts.order import Order
from cow_py.composable.types import PollParams, PollResultCode, PollResultError

# Constants
OWNER = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
SALT = HexStr("0xd98a87ed4e45bfeae3f779e1ac09ceacdfb57da214c7fffa6434aeb969f396c0")
SALT_2 = HexStr("0xd98a87ed4e45bfeae3f779e1ac09ceacdfb57da214c7fffa6434aeb969f396c1")
TWAP_ID = "0xd8a6889486a47d8ca8f4189f11573b39dbc04f605719ebf4050e44ae53c1bedf"
TWAP_ID_2 = "0x8ddb7e8e1cd6a06d5bb6f91af21a2b26a433a5d8402ccddb00a72e4006c46994"

ONE_ETHER = Web3.to_wei(1, "ether")
ZERO_ADDRESS = Web3.to_checksum_address("0x0000000000000000000000000000000000000000")

# Test data
TWAP_PARAMS_TEST = TwapData(
    sell_token="0x6810e776880C02933D47DB1b9fc05908e5386b96",
    buy_token="0xDAE5F1590db13E3B40423B5b5c5fbf175515910b",
    receiver="0xDeaDbeefdEAdbeefdEadbEEFdeadbeEFdEaDbeeF",
    sell_amount=ONE_ETHER,
    buy_amount=ONE_ETHER,
    time_between_parts=3600,  # 1 hour in seconds
    number_of_parts=10,
    duration_type=DurationType.AUTO,
    start_type=StartType.AT_MINING_TIME,
    app_data="0xd51f28edffcaaa76be4a22f6375ad289272c037f3cc072345676e88d92ced8b5",
    start_time_epoch=0,
    duration_of_part=0,
)


class TestTwapConstructor:
    def test_create_new_valid_twap(self):
        twap = Twap(handler=TWAP_ADDRESS, data=TWAP_PARAMS_TEST)
        assert twap.order_type == "twap"
        assert not twap.has_off_chain_input
        assert twap.off_chain_input == "0x"
        assert twap.context is not None
        assert twap.context.address is not None

    def test_create_twap_with_invalid_handler(self):
        with pytest.raises(ValueError, match="InvalidHandler"):
            Twap(
                handler=HexStr("0xdeaddeaddeaddeaddeaddeaddeaddeaddeaddead"),
                data=TWAP_PARAMS_TEST,
            )


class TestTwapFromData:
    def test_creates_valid_twap_start_at_mining_time(self):
        twap = Twap.from_data(TWAP_PARAMS_TEST)
        assert twap.order_type == "twap"
        assert not twap.has_off_chain_input
        assert twap.off_chain_input == "0x"
        assert twap.context is not None
        assert twap.context.address is not None

    def test_creates_valid_twap_start_at_epoch(self):
        test_data = TwapData(
            **{
                **TWAP_PARAMS_TEST.__dict__,
                "start_type": StartType.AT_EPOCH,
                "start_time_epoch": 1,
            }
        )
        twap = Twap.from_data(test_data)
        assert twap.context is None


class TestTwapId:
    def test_id_is_computed_correctly(self):
        twap = Twap.from_data(TWAP_PARAMS_TEST, SALT)
        assert twap.id == TWAP_ID

    def test_id_doesnt_change_for_same_params_and_salt(self):
        twap1 = Twap.from_data(TWAP_PARAMS_TEST, SALT)
        twap2 = Twap.from_data(TWAP_PARAMS_TEST, SALT)
        assert twap1.id == twap2.id

    def test_id_changes_for_same_params_and_different_salt(self):
        twap1 = Twap.from_data(TWAP_PARAMS_TEST, SALT)
        twap2 = Twap.from_data(TWAP_PARAMS_TEST, SALT_2)
        assert twap1.id != twap2.id
        assert twap2.id == TWAP_ID_2

    def test_id_changes_for_different_params_and_same_salt(self):
        test_data = TwapData(
            **{
                **TWAP_PARAMS_TEST.__dict__,
                "start_type": StartType.AT_EPOCH,
                "start_time_epoch": 123456789,
            }
        )
        twap = Twap.from_data(test_data, SALT)
        assert (
            twap.id
            == "0xe993544057dbc8504c4e38a6fe35845a81e0849c11242a6070f9d25152598df6"
        )


class TestTwapValidate:
    def test_valid_twap(self):
        assert Twap.from_data(TWAP_PARAMS_TEST).is_valid().is_valid

    def test_invalid_twap_same_token(self):
        test_data = TwapData(
            **{**TWAP_PARAMS_TEST.__dict__, "sell_token": TWAP_PARAMS_TEST.buy_token}
        )
        assert asdict(Twap.from_data(test_data).is_valid()) == {
            "is_valid": False,
            "reason": "InvalidSameToken",
        }

    def test_invalid_twap_zero_sell_token(self):
        test_data = TwapData(
            **{**TWAP_PARAMS_TEST.__dict__, "sell_token": ZERO_ADDRESS}
        )
        assert asdict(Twap.from_data(test_data).is_valid()) == {
            "is_valid": False,
            "reason": "InvalidToken",
        }

    def test_invalid_twap_zero_sell_amount(self):
        test_data = TwapData(**{**TWAP_PARAMS_TEST.__dict__, "sell_amount": 0})
        assert asdict(Twap.from_data(test_data).is_valid()) == {
            "is_valid": False,
            "reason": "InvalidSellAmount",
        }

    def test_invalid_twap_zero_buy_amount(self):
        test_data = TwapData(**{**TWAP_PARAMS_TEST.__dict__, "buy_amount": 0})
        assert asdict(Twap.from_data(test_data).is_valid()) == {
            "is_valid": False,
            "reason": "InvalidMinBuyAmount",
        }

    def test_invalid_twap_start_time(self):
        test_data = TwapData(
            **{
                **TWAP_PARAMS_TEST.__dict__,
                "start_type": StartType.AT_EPOCH,
                "start_time_epoch": -1,
            }
        )
        assert asdict(Twap.from_data(test_data).is_valid()) == {
            "is_valid": False,
            "reason": "InvalidStartTime",
        }

    def test_invalid_twap_zero_parts(self):
        test_data = TwapData(**{**TWAP_PARAMS_TEST.__dict__, "number_of_parts": 0})
        assert asdict(Twap.from_data(test_data).is_valid()) == {
            "is_valid": False,
            "reason": "InvalidNumParts",
        }

    def test_invalid_twap_frequency(self):
        test_data = TwapData(**{**TWAP_PARAMS_TEST.__dict__, "time_between_parts": 0})
        assert asdict(Twap.from_data(test_data).is_valid()) == {
            "is_valid": False,
            "reason": "InvalidFrequency",
        }

    def test_invalid_twap_limit_duration_span(self):
        test_data = TwapData(
            **{
                **TWAP_PARAMS_TEST.__dict__,
                "duration_type": DurationType.LIMIT_DURATION,
                "duration_of_part": TWAP_PARAMS_TEST.time_between_parts + 1,
            }
        )
        assert asdict(Twap.from_data(test_data).is_valid()) == {
            "is_valid": False,
            "reason": "InvalidSpan",
        }


class TestTwapSerialization:
    def test_serialization_deserialization(self):
        twap = Twap.from_data(TWAP_PARAMS_TEST)
        serialized = twap.serialize()
        deserialized = Twap.deserialize(serialized)
        assert deserialized.id == twap.id


# @pytest.mark.asyncio
# class TestTwapPollValidate:
#     @pytest.fixture
#     def setup(self):
#         block_number = 123456
#         block_timestamp = 1700000000
#         mock_order_book = AsyncMock()
#         mock_cabinet = AsyncMock()
#         mock_end_timestamp = Mock()

#         provider = AsyncMock()
#         provider.eth = AsyncMock()
#         provider.eth.get_block = AsyncMock()

#         poll_params = PollParams(
#             owner=OWNER,
#             provider=provider,
#             chain=Chain.MAINNET,
#             order_book_api=mock_order_book,
#             block_info={"number": block_number, "timestamp": block_timestamp},  # type: ignore
#         )

#         return {
#             "block_number": block_number,
#             "block_timestamp": block_timestamp,
#             "mock_cabinet": mock_cabinet,
#             "mock_end_timestamp": mock_end_timestamp,
#             "provider": provider,
#             "poll_params": poll_params,
#         }

#     async def test_open_twap_passes_validations(self, setup):
#         twap = Twap.from_data(TWAP_PARAMS_TEST)
#         twap.cabinet = setup["mock_cabinet"]
#         twap.end_timestamp = setup["mock_end_timestamp"]

#         setup["mock_cabinet"].return_value = setup["block_timestamp"] - 1
#         setup["mock_end_timestamp"].return_value = setup["block_timestamp"] + 1

#         result = await twap.poll_validate(setup["poll_params"])
#         assert result is None
#         setup["mock_cabinet"].assert_called_once()

#     async def test_twap_has_not_started(self, setup):
#         start_time = setup["block_timestamp"] + 1
#         twap = Twap.from_data(TWAP_PARAMS_TEST)
#         twap.cabinet = setup["mock_cabinet"]
#         twap.end_timestamp = setup["mock_end_timestamp"]

#         setup["mock_cabinet"].return_value = start_time
#         setup["mock_end_timestamp"].return_value = setup["block_timestamp"] + 2

#         result = await twap.poll_validate(setup["poll_params"])
#         assert isinstance(result, PollResultError)
#         assert result.result == PollResultCode.TRY_AT_EPOCH
#         assert result.epoch == start_time
#         assert "TWAP hasn't started yet" in result.reason

#     async def test_twap_has_expired(self, setup):
#         expire_time = setup["block_timestamp"] - 1
#         twap = Twap.from_data(TWAP_PARAMS_TEST)
#         twap.cabinet = setup["mock_cabinet"]
#         twap.end_timestamp = lambda _: expire_time  # type: ignore

#         setup["mock_cabinet"].return_value = setup["block_timestamp"] - 2

#         result = await twap.poll_validate(setup["poll_params"])
#         assert isinstance(result, PollResultError)
#         assert result.result == PollResultCode.DONT_TRY_AGAIN
#         assert "TWAP has expired" in result.reason

#     async def test_cabinet_overflow(self, setup):
#         twap = Twap.from_data(TWAP_PARAMS_TEST)
#         twap.cabinet = setup["mock_cabinet"]

#         setup["mock_cabinet"].return_value = 2**32  # Overflow uint32

#         result = await twap.poll_validate(setup["poll_params"])
#         assert isinstance(result, PollResultError)
#         assert result.result == PollResultCode.DONT_TRY_AGAIN
#         assert "Cabinet epoch out of range" in result.reason


# class TestTwapToString:
#     def test_to_string_start_time_at_epoch(self):
#         test_data = TwapData(
#             **{
#                 **TWAP_PARAMS_TEST.__dict__,
#                 "start_type": StartType.AT_EPOCH,
#                 "start_time_epoch": 1692876646,
#             }
#         )
#         twap = Twap.from_data(test_data, SALT)
#         expected_id = (
#             "0x28b19554c54f10b67f6ef7e72bdc552fb865b12d33b797ac51227768705fff0d"
#         )
#         result = twap.to_string()
#         assert result.startswith(f"twap ({expected_id}): ")
#         print(result)
#         assert '"startTime": 1692876646' in result

#     def test_to_string_limit_duration(self):
#         test_data = TwapData(
#             **{
#                 **TWAP_PARAMS_TEST.__dict__,
#                 "duration_type": DurationType.LIMIT_DURATION,
#                 "duration_of_part": 1000,
#             }
#         )
#         twap = Twap.from_data(test_data, SALT)
#         result = twap.to_string()
#         expected_id = (
#             "0x7352e87b6e5d7c4e27479a13b7ba8bc0d67a947d1692994bd995c9dcc94c166a"
#         )
#         assert result.startswith(f"twap ({expected_id}): ")
#         assert '"durationOfPart": 1000' in result


# @pytest.mark.asyncio
# class TestCurrentTwapPartInOrderBook:
#     @pytest.fixture
#     def setup(self):
#         block_number = 123456
#         start_timestamp = 1700000000
#         time_between_parts = 100
#         number_of_parts = 10
#         total_duration = time_between_parts * number_of_parts
#         order_id = "0x1"
#         order = Mock(spec=Order)

#         return {
#             "block_number": block_number,
#             "start_timestamp": start_timestamp,
#             "time_between_parts": time_between_parts,
#             "number_of_parts": number_of_parts,
#             "total_duration": total_duration,
#             "order_id": order_id,
#             "order": order,
#         }

#     def get_twap_for_test(self, setup):
#         return Twap.from_data(
#             TwapData(
#                 **{
#                     **TWAP_PARAMS_TEST.__dict__,
#                     "time_between_parts": setup["time_between_parts"],
#                     "number_of_parts": setup["number_of_parts"],
#                     "start_type": StartType.AT_EPOCH,
#                     "start_time_epoch": setup["start_timestamp"],
#                 }
#             )
#         )

#     async def test_polling_at_start_of_part_1(self, setup):
#         twap = self.get_twap_for_test(setup)
#         params = PollParams(
#             owner=OWNER,
#             provider=Mock(),
#             chain=Chain.MAINNET,
#             order_book_api=AsyncMock(),
#             block_info={
#                 "number": setup["block_number"],
#                 "timestamp": setup["start_timestamp"],
#             },
#         )

#         twap.get_block_timestamp = setup["start_timestamp"]
#         twap.


#         result = await twap.handle_poll_failed_already_present(
#             setup["order_id"], setup["order"], params
#         )

#         assert isinstance(result, PollResultError)
#         assert result.result == PollResultCode.TRY_AT_EPOCH
#         assert result.epoch == setup["start_timestamp"] + setup["time_between_parts"]
#         assert "Current active TWAP part (1/10)" in result.reason

#     async def test_polling_at_middle_of_part_1(self, setup):
#         mid_part_time = setup["start_timestamp"] + setup["time_between_parts"] // 2
#         twap = self.get_twap_for_test(setup)
#         params = PollParams(
#             owner=OWNER,
#             chain=Chain.MAINNET,
#             order_book_api=AsyncMock(),
#             provider=Mock(),
#             block_info={"number": setup["block_number"], "timestamp": mid_part_time},
#         )

#         result = await twap.handle_poll_failed_already_present(
#             setup["order_id"], setup["order"], params
#         )

#         assert isinstance(result, PollResultError)
#         assert result.result == PollResultCode.TRY_AT_EPOCH
#         assert result.epoch == setup["start_timestamp"] + setup["time_between_parts"]
#         assert "Current active TWAP part (1/10)" in result.reason

#     async def test_polling_at_last_part(self, setup):
#         last_part_start = (
#             setup["start_timestamp"]
#             + (setup["number_of_parts"] - 1) * setup["time_between_parts"]
#         )
#         twap = self.get_twap_for_test(setup)
#         params = PollParams(
#             owner=OWNER,
#             provider=Mock(),
#             chain=Chain.MAINNET,
#             order_book_api=AsyncMock(),
#             block_info={"number": setup["block_number"], "timestamp": last_part_start},
#         )

#         result = await twap.handle_poll_failed_already_present(
#             setup["order_id"], setup["order"], params
#         )

#         assert isinstance(result, PollResultError)
#         assert result.result == PollResultCode.DONT_TRY_AGAIN
#         assert "This was the last TWAP part" in result.reason

#     async def test_polling_twap_not_started(self, setup):
#         not_started_time = setup["start_timestamp"] - 1
#         twap = self.get_twap_for_test(setup)
#         params = PollParams(
#             owner=OWNER,
#             provider=Mock(),
#             chain=Chain.MAINNET,
#             order_book_api=AsyncMock(),
#             block_info={"number": setup["block_number"], "timestamp": not_started_time},
#         )

#         result = await twap.handle_poll_failed_already_present(
#             setup["order_id"], setup["order"], params
#         )

#         assert isinstance(result, PollResultError)
#         assert result.result == PollResultCode.UNEXPECTED_ERROR
#         assert "TWAP hasn't started yet" in result.reason

#     async def test_polling_twap_expired(self, setup):
#         expired_time = setup["start_timestamp"] + setup["total_duration"] + 1
#         twap = self.get_twap_for_test(setup)
#         params = PollParams(
#             owner=OWNER,
#             provider=Mock(),
#             chain=Chain.MAINNET,
#             order_book_api=AsyncMock(),
#             block_info={"number": setup["block_number"], "timestamp": expired_time},
#         )

#         result = await twap.handle_poll_failed_already_present(
#             setup["order_id"], setup["order"], params
#         )

#         assert isinstance(result, PollResultError)
#         assert result.result == PollResultCode.UNEXPECTED_ERROR
#         assert "TWAP is expired" in result.reason


# def uint256_helper(n: int) -> str:
#     return Web3.to_hex(Web3.to_bytes(n).rjust(32, b"\x00"))


@pytest.mark.asyncio
class TestCurrentTwapPartInOrderBook:
    @pytest.fixture
    def setup(self):
        block_number = 123456
        start_timestamp = 1700000000
        time_between_parts = 100
        number_of_parts = 10
        total_duration = time_between_parts * number_of_parts
        order_id = "0x1"
        order = Mock(spec=Order)

        # Mock setup
        mock_order_book = AsyncMock()
        mock_cabinet = AsyncMock()
        mock_end_timestamp = Mock()

        provider = AsyncMock()
        provider.eth = AsyncMock()
        provider.eth.get_block = AsyncMock()

        class MockTwap(Twap):
            cabinet = mock_cabinet
            end_timestamp = mock_end_timestamp

        return {
            "block_number": block_number,
            "start_timestamp": start_timestamp,
            "time_between_parts": time_between_parts,
            "number_of_parts": number_of_parts,
            "total_duration": total_duration,
            "order_id": order_id,
            "order": order,
            "mock_cabinet": mock_cabinet,
            "mock_end_timestamp": mock_end_timestamp,
            "mock_order_book": mock_order_book,
            "provider": provider,
            "MockTwap": MockTwap,
        }

    def get_twap_for_test(self, setup):
        test_data = TwapData(
            **{
                **TWAP_PARAMS_TEST.__dict__,
                "time_between_parts": setup["time_between_parts"],
                "number_of_parts": setup["number_of_parts"],
                "start_type": StartType.AT_EPOCH,
                "start_time_epoch": setup["start_timestamp"],
            }
        )
        return setup["MockTwap"](handler=TWAP_ADDRESS, data=test_data)

    async def test_polling_at_start_of_part_1(self, setup):
        twap = self.get_twap_for_test(setup)
        params = PollParams(
            owner=OWNER,
            provider=setup["provider"],
            chain=Chain.MAINNET,
            order_book_api=setup["mock_order_book"],
            block_info={
                "number": setup["block_number"],
                "timestamp": setup["start_timestamp"],
            },  # type: ignore
        )

        setup["mock_cabinet"].return_value = uint256_helper(setup["start_timestamp"])
        setup["mock_end_timestamp"].return_value = (
            setup["start_timestamp"] + setup["time_between_parts"]
        )

        result = await twap.handle_poll_failed_already_present(
            setup["order_id"], setup["order"], params
        )

        assert isinstance(result, PollResultError)
        assert result.result == PollResultCode.TRY_AT_EPOCH
        assert result.epoch == setup["start_timestamp"] + setup["time_between_parts"]
        assert "Current active TWAP part (1/10)" in result.reason

    async def test_polling_at_middle_of_part_1(self, setup):
        mid_part_time = setup["start_timestamp"] + setup["time_between_parts"] // 2
        twap = self.get_twap_for_test(setup)
        params = PollParams(
            owner=OWNER,
            provider=setup["provider"],
            chain=Chain.MAINNET,
            order_book_api=setup["mock_order_book"],
            block_info={"number": setup["block_number"], "timestamp": mid_part_time},  # type: ignore
        )

        setup["mock_cabinet"].return_value = uint256_helper(setup["start_timestamp"])
        setup["mock_end_timestamp"].return_value = (
            setup["start_timestamp"] + setup["time_between_parts"]
        )

        result = await twap.handle_poll_failed_already_present(
            setup["order_id"], setup["order"], params
        )

        assert isinstance(result, PollResultError)
        assert result.result == PollResultCode.TRY_AT_EPOCH
        assert result.epoch == setup["start_timestamp"] + setup["time_between_parts"]
        assert "Current active TWAP part (1/10)" in result.reason

    async def test_polling_at_last_part(self, setup):
        last_part_start = (
            setup["start_timestamp"]
            + (setup["number_of_parts"] - 1) * setup["time_between_parts"]
        )
        twap = self.get_twap_for_test(setup)
        params = PollParams(
            owner=OWNER,
            provider=setup["provider"],
            chain=Chain.MAINNET,
            order_book_api=setup["mock_order_book"],
            block_info={"number": setup["block_number"], "timestamp": last_part_start},  # type: ignore
        )

        setup["mock_cabinet"].return_value = uint256_helper(setup["start_timestamp"])
        setup["mock_end_timestamp"].return_value = (
            setup["start_timestamp"] + setup["total_duration"]
        )

        result = await twap.handle_poll_failed_already_present(
            setup["order_id"], setup["order"], params
        )

        assert isinstance(result, PollResultError)
        assert result.result == PollResultCode.DONT_TRY_AGAIN
        assert "This was the last TWAP part" in result.reason

    async def test_polling_twap_not_started(self, setup):
        not_started_time = setup["start_timestamp"] - 1
        twap = self.get_twap_for_test(setup)
        params = PollParams(
            owner=OWNER,
            provider=setup["provider"],
            chain=Chain.MAINNET,
            order_book_api=setup["mock_order_book"],
            block_info={"number": setup["block_number"], "timestamp": not_started_time},  # type: ignore
        )

        setup["mock_cabinet"].return_value = uint256_helper(setup["start_timestamp"])
        setup["mock_end_timestamp"].return_value = (
            setup["start_timestamp"] + setup["time_between_parts"]
        )

        result = await twap.handle_poll_failed_already_present(
            setup["order_id"], setup["order"], params
        )

        assert isinstance(result, PollResultError)
        assert result.result == PollResultCode.UNEXPECTED_ERROR
        assert "TWAP hasn't started yet" in result.reason

    async def test_polling_twap_expired(self, setup):
        expired_time = setup["start_timestamp"] + setup["total_duration"] + 1
        twap = self.get_twap_for_test(setup)
        params = PollParams(
            owner=OWNER,
            provider=setup["provider"],
            chain=Chain.MAINNET,
            order_book_api=setup["mock_order_book"],
            block_info={"number": setup["block_number"], "timestamp": expired_time},  # type: ignore
        )

        setup["mock_cabinet"].return_value = uint256_helper(setup["start_timestamp"])
        setup["mock_end_timestamp"].return_value = (
            setup["start_timestamp"] + setup["total_duration"]
        )

        result = await twap.handle_poll_failed_already_present(
            setup["order_id"], setup["order"], params
        )

        assert isinstance(result, PollResultError)
        assert result.result == PollResultCode.UNEXPECTED_ERROR
        assert "TWAP is expired" in result.reason


def uint256_helper(n: int) -> str:
    return Web3.to_hex(Web3.to_bytes(n).rjust(32, b"\x00"))[2:]
