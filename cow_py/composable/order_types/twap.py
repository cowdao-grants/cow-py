from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Dict, Any, Optional
from web3 import Web3

from ..conditional_order import ConditionalOrder
from ..types import IsValidResult, PollParams, PollResultCode, GPv2OrderStruct
from ..utils import format_epoch

TWAP_ADDRESS = "0x6cF1e9cA41f7611dEf408122793c358a3d11E5a5"
CURRENT_BLOCK_TIMESTAMP_FACTORY_ADDRESS = "0x52eD56Da04309Aca4c3FECC595298d80C2f16BAc"


class DurationType(Enum):
    AUTO = "AUTO"
    LIMIT_DURATION = "LIMIT_DURATION"


class StartTimeValue(Enum):
    AT_MINING_TIME = "AT_MINING_TIME"
    AT_EPOCH = "AT_EPOCH"


@dataclass
class TwapData:
    sell_token: str
    buy_token: str
    receiver: str
    sell_amount: int
    buy_amount: int
    start_time: Dict[str, Any]
    number_of_parts: int
    time_between_parts: int
    duration_of_part: Dict[str, Any]
    app_data: str


@dataclass
class TwapStruct:
    sell_token: str
    buy_token: str
    receiver: str
    part_sell_amount: int
    min_part_limit: int
    t0: int
    n: int
    t: int
    span: int
    app_data: str


class Twap(ConditionalOrder[TwapData, TwapStruct]):
    def __init__(self, handler: str, data: TwapData, salt: Optional[str] = None):
        if handler != TWAP_ADDRESS:
            raise ValueError(
                f"InvalidHandler: Expected: {TWAP_ADDRESS}, provided: {handler}"
            )
        super().__init__(
            handler,
            salt or Web3.keccak(text=Web3.to_hex(Web3.random.randbytes(32))).hex(),
            data,
        )

    @property
    def is_single_order(self) -> bool:
        return True

    @property
    def order_type(self) -> str:
        return "twap"

    @property
    def context(self) -> Optional[Dict[str, Any]]:
        if self.static_input.t0 > 0:
            return super().context
        else:
            return {
                "address": CURRENT_BLOCK_TIMESTAMP_FACTORY_ADDRESS,
                "factory_args": None,
            }

    def is_valid(self) -> IsValidResult:
        data = self.data
        error = None

        if data.sell_token == data.buy_token:
            error = "InvalidSameToken"
        elif data.sell_token == Web3.to_checksum_address(
            "0x0000000000000000000000000000000000000000"
        ) or data.buy_token == Web3.to_checksum_address(
            "0x0000000000000000000000000000000000000000"
        ):
            error = "InvalidToken"
        elif not data.sell_amount > 0:
            error = "InvalidSellAmount"
        elif not data.buy_amount > 0:
            error = "InvalidMinBuyAmount"
        elif data.start_time.get("startType") == StartTimeValue.AT_EPOCH.value:
            t0 = data.start_time["epoch"]
            if not (0 <= t0 < 2**32):
                error = "InvalidStartTime"
        elif not (1 < data.number_of_parts <= 2**32):
            error = "InvalidNumParts"
        elif not (0 < data.time_between_parts <= 365 * 24 * 60 * 60):
            error = "InvalidFrequency"
        elif (
            data.duration_of_part.get("durationType")
            == DurationType.LIMIT_DURATION.value
        ):
            if not data.duration_of_part["duration"] <= data.time_between_parts:
                error = "InvalidSpan"

        if not error:
            try:
                self.encode_static_input()
            except Exception:
                error = "InvalidData"

        return (
            {"is_valid": not bool(error), "reason": error}
            if error
            else {"is_valid": True}
        )

    def serialize(self) -> str:
        return Web3.to_hex(Web3.keccak(text=str(self.data)))

    def encode_static_input(self) -> str:
        return Web3.to_hex(Web3.keccak(text=str(self.static_input)))

    @classmethod
    def deserialize(cls, twap_serialized: str) -> "Twap":
        # Implement deserialize logic here
        pass

    def to_string(self, token_formatter=None) -> str:
        data = self.data
        start_time = (
            "AT_MINING_TIME"
            if data.start_time["startType"] == StartTimeValue.AT_MINING_TIME.value
            else data.start_time["epoch"]
        )
        duration_of_part = (
            "AUTO"
            if data.duration_of_part["durationType"] == DurationType.AUTO.value
            else data.duration_of_part["duration"]
        )

        details = {
            "sellAmount": str(data.sell_amount),
            "sellToken": data.sell_token,
            "buyAmount": str(data.buy_amount),
            "buyToken": data.buy_token,
            "numberOfParts": str(data.number_of_parts),
            "startTime": start_time,
            "timeBetweenParts": data.time_between_parts,
            "durationOfPart": duration_of_part,
            "receiver": data.receiver,
            "appData": data.app_data,
        }

        return f"{self.order_type} ({self.id}): {str(details)}"

    def transform_data_to_struct(self, data: TwapData) -> TwapStruct:
        sell_amount = Decimal(data.sell_amount)
        buy_amount = Decimal(data.buy_amount)
        number_of_parts = Decimal(data.number_of_parts)

        part_sell_amount = sell_amount // number_of_parts
        min_part_limit = buy_amount // number_of_parts

        span = (
            0
            if data.duration_of_part["durationType"] == DurationType.AUTO.value
            else data.duration_of_part["duration"]
        )
        t0 = (
            0
            if data.start_time["startType"] == StartTimeValue.AT_MINING_TIME.value
            else data.start_time["epoch"]
        )

        return TwapStruct(
            sell_token=data.sell_token,
            buy_token=data.buy_token,
            receiver=data.receiver,
            part_sell_amount=int(part_sell_amount),
            min_part_limit=int(min_part_limit),
            t0=int(t0),
            n=int(data.number_of_parts),
            t=int(data.time_between_parts),
            span=int(span),
            app_data=data.app_data,
        )

    def transform_struct_to_data(self, struct: TwapStruct) -> TwapData:
        number_of_parts = Decimal(struct.n)
        sell_amount = Decimal(struct.part_sell_amount) * number_of_parts
        buy_amount = Decimal(struct.min_part_limit) * number_of_parts

        duration_of_part = (
            {"durationType": DurationType.AUTO.value}
            if struct.span == 0
            else {
                "durationType": DurationType.LIMIT_DURATION.value,
                "duration": struct.span,
            }
        )

        start_time = (
            {"startType": StartTimeValue.AT_MINING_TIME.value}
            if struct.t0 == 0
            else {"startType": StartTimeValue.AT_EPOCH.value, "epoch": struct.t0}
        )

        return TwapData(
            sell_token=struct.sell_token,
            buy_token=struct.buy_token,
            receiver=struct.receiver,
            sell_amount=int(sell_amount),
            buy_amount=int(buy_amount),
            start_time=start_time,
            number_of_parts=int(number_of_parts),
            time_between_parts=struct.t,
            duration_of_part=duration_of_part,
            app_data=struct.app_data,
        )

    async def poll_validate(self, params: PollParams) -> Optional[Dict[str, Any]]:
        block_info = params.get("block_info") or await self.get_block_info(
            params["provider"]
        )
        block_timestamp = block_info["block_timestamp"]

        try:
            start_timestamp = await self.start_timestamp(params)

            if start_timestamp > block_timestamp:
                return {
                    "result": PollResultCode.TRY_AT_EPOCH,
                    "epoch": start_timestamp,
                    "reason": f"TWAP hasn't started yet. Starts at {start_timestamp} ({format_epoch(start_timestamp)})",
                }

            expiration_timestamp = self.end_timestamp(start_timestamp)
            if block_timestamp >= expiration_timestamp:
                return {
                    "result": PollResultCode.DONT_TRY_AGAIN,
                    "reason": f"TWAP has expired. Expired at {expiration_timestamp} ({format_epoch(expiration_timestamp)})",
                }

            return None
        except Exception as err:
            if "Cabinet is not set" in str(err):
                return {
                    "result": PollResultCode.DONT_TRY_AGAIN,
                    "reason": f"{str(err)}. User likely removed the order.",
                }
            elif "Cabinet epoch out of range" in str(err):
                return {
                    "result": PollResultCode.DONT_TRY_AGAIN,
                    "reason": str(err),
                }

            return {
                "result": PollResultCode.UNEXPECTED_ERROR,
                "reason": f"Unexpected error: {str(err)}",
                "error": err,
            }

    async def handle_poll_failed_already_present(
        self, order_uid: str, order: GPv2OrderStruct, params: PollParams
    ) -> Optional[Dict[str, Any]]:
        block_info = params.get("block_info") or await self.get_block_info(
            params["provider"]
        )
        block_timestamp = block_info["block_timestamp"]

        time_between_parts = self.data.time_between_parts
        number_of_parts = self.data.number_of_parts
        start_timestamp = await self.start_timestamp(params)

        if block_timestamp < start_timestamp:
            return {
                "result": PollResultCode.UNEXPECTED_ERROR,
                "reason": f"TWAP part hasn't started. First TWAP part starts at {start_timestamp} ({format_epoch(start_timestamp)})",
                "error": None,
            }

        expire_time = number_of_parts * time_between_parts + start_timestamp
        if block_timestamp >= expire_time:
            return {
                "result": PollResultCode.UNEXPECTED_ERROR,
                "reason": f"TWAP is expired. Expired at {expire_time} ({format_epoch(expire_time)})",
                "error": None,
            }

        current_part_number = (block_timestamp - start_timestamp) // time_between_parts

        if current_part_number == number_of_parts - 1:
            return {
                "result": PollResultCode.DONT_TRY_AGAIN,
                "reason": f"Current active TWAP part ({current_part_number + 1}/{number_of_parts}) is already in the Order Book. This was the last TWAP part, no more orders need to be placed",
            }

        next_part_start_time = (
            start_timestamp + (current_part_number + 1) * time_between_parts
        )

        return {
            "result": PollResultCode.TRY_AT_EPOCH,
            "epoch": next_part_start_time,
            "reason": f"Current active TWAP part ({current_part_number + 1}/{number_of_parts}) is already in the Order Book. TWAP part {current_part_number + 2} doesn't start until {next_part_start_time} ({format_epoch(next_part_start_time)})",
        }

    async def start_timestamp(self, params: Dict[str, Any]) -> int:
        start_time = self.data.start_time

        if start_time["startType"] == StartTimeValue.AT_EPOCH.value:
            return int(start_time["epoch"])

        cabinet = await self.cabinet(params)
        raw_cabinet_epoch = Web3.to_int(hexstr=cabinet)

        if raw_cabinet_epoch > 2**32 - 1:
            raise ValueError(f"Cabinet epoch out of range: {raw_cabinet_epoch}")

        cabinet_epoch = int(raw_cabinet_epoch)

        if cabinet_epoch == 0:
            raise ValueError(
                "Cabinet is not set. Required for TWAP orders that start at mining time."
            )

        return cabinet_epoch

    def end_timestamp(self, start_timestamp: int) -> int:
        number_of_parts = self.data.number_of_parts
        time_between_parts = self.data.time_between_parts
        duration_of_part = self.data.duration_of_part

        if duration_of_part["durationType"] == DurationType.LIMIT_DURATION.value:
            return (
                start_timestamp
                + (number_of_parts - 1) * time_between_parts
                + duration_of_part["duration"]
            )

        return start_timestamp + number_of_parts * time_between_parts

    @staticmethod
    async def get_block_info(provider: Any) -> Dict[str, int]:
        latest_block = await provider.eth.get_block("latest")
        return {
            "block_number": latest_block["number"],
            "block_timestamp": latest_block["timestamp"],
        }
