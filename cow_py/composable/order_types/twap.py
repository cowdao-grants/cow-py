from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
import json
from typing import Dict, Any, Optional, Tuple
from eth_typing import HexStr
from hexbytes import HexBytes
from web3 import Web3
from eth_abi.abi import encode

from cowdao_cowpy.contracts.order import Order


from ..conditional_order import ConditionalOrder
from ..types import (
    ContextFactory,
    IsValidResult,
    PollParams,
    PollResultCode,
    PollResultError,
)
from ..utils import encode_params, format_epoch

TWAP_ADDRESS = HexStr("0x6cF1e9cA41f7611dEf408122793c358a3d11E5a5")
CURRENT_BLOCK_TIMESTAMP_FACTORY_ADDRESS = "0x52eD56Da04309Aca4c3FECC595298d80C2f16BAc"


TWAP_STRUCT_ABI = [
    "(address,address,address,uint256,uint256,uint256,uint256,uint256,uint256,bytes32)"
]

TWAP_STRUCT_TYPE = Tuple[str, str, str, int, int, int, int, int, int, bytes]


class DurationType(Enum):
    AUTO = "AUTO"
    LIMIT_DURATION = "LIMIT_DURATION"


class StartType(Enum):
    AT_MINING_TIME = "AT_MINING_TIME"
    AT_EPOCH = "AT_EPOCH"


@dataclass
class TwapData:
    sell_token: str
    buy_token: str
    receiver: str
    sell_amount: int
    buy_amount: int
    start_type: StartType
    number_of_parts: int
    time_between_parts: int
    duration_type: DurationType
    app_data: str
    start_time_epoch: int = 0
    duration_of_part: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sellToken": self.sell_token,
            "buyToken": self.buy_token,
            "receiver": self.receiver,
            "sellAmount": self.sell_amount,
            "buyAmount": self.buy_amount,
            "startType": self.start_type.value,
            "numberOfParts": self.number_of_parts,
            "timeBetweenParts": self.time_between_parts,
            "durationType": self.duration_type.value,
            "appData": self.app_data,
            "startTimeEpoch": self.start_time_epoch,
            "durationOfPart": self.duration_of_part,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "TwapData":
        return TwapData(
            sell_token=d["sellToken"],
            buy_token=d["buyToken"],
            receiver=d["receiver"],
            sell_amount=d["sellAmount"],
            buy_amount=d["buyAmount"],
            start_type=StartType(d["startType"]),
            number_of_parts=d["numberOfParts"],
            time_between_parts=d["timeBetweenParts"],
            duration_type=DurationType(d["durationType"]),
            app_data=d["appData"],
            start_time_epoch=d["startTimeEpoch"],
            duration_of_part=d["durationOfPart"],
        )


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
    def __init__(self, handler: HexStr, data: TwapData, salt: Optional[HexStr] = None):
        if handler != TWAP_ADDRESS:
            raise ValueError(
                f"InvalidHandler: Expected: {TWAP_ADDRESS}, provided: {handler}"
            )
        super().__init__(
            handler,
            data,
            salt,
        )

    @staticmethod
    def from_data_dict(data: Dict[str, Any]) -> "Twap":
        return Twap.from_data(TwapData.from_dict(data), salt=HexStr(data["salt"]))

    @staticmethod
    def from_data(data: TwapData, salt: Optional[HexStr] = None) -> "Twap":
        return Twap(TWAP_ADDRESS, data, salt)

    @property
    def is_single_order(self) -> bool:
        return True

    @property
    def order_type(self) -> str:
        return "twap"

    @property
    def context(self) -> Optional[ContextFactory]:
        if self.static_input.t0 > 0:
            return super().context
        else:
            return ContextFactory(
                address=CURRENT_BLOCK_TIMESTAMP_FACTORY_ADDRESS,
                factory_args=None,
            )

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
        elif data.start_type == StartType.AT_EPOCH:
            t0 = data.start_time_epoch
            if not (0 <= t0 < 2**32):
                error = "InvalidStartTime"
        elif not (1 < data.number_of_parts <= 2**32):
            error = "InvalidNumParts"
        elif not (0 < data.time_between_parts <= 365 * 24 * 60 * 60):
            error = "InvalidFrequency"
        elif data.duration_type == DurationType.LIMIT_DURATION:
            if not data.duration_of_part <= data.time_between_parts:
                error = "InvalidSpan"

        if not error:
            try:
                self.encode_static_input()
            except Exception:
                error = "InvalidData"

        return (
            IsValidResult(is_valid=False, reason=error)
            if error
            else IsValidResult(is_valid=True)
        )

    def serialize(self) -> HexStr:
        return encode_params(self.leaf)

    def encode_static_input(self) -> HexStr:
        return Web3.to_hex(
            encode(
                TWAP_STRUCT_ABI,
                [
                    [
                        self.static_input.sell_token,
                        self.static_input.buy_token,
                        self.static_input.receiver,
                        self.static_input.part_sell_amount,
                        self.static_input.min_part_limit,
                        self.static_input.t0,
                        self.static_input.n,
                        self.static_input.t,
                        self.static_input.span,
                        HexBytes(self.static_input.app_data),
                    ]
                ],
            )
        )

    @staticmethod
    def deserialize(twap_serialized: HexStr) -> "Twap":
        return Twap.deserialize_helper(
            twap_serialized, TWAP_ADDRESS, TWAP_STRUCT_ABI, Twap.deserialize_callback
        )

    async def get_block_timestamp(self, params: PollParams) -> int:
        block_info = params.block_info or await params.provider.eth.get_block("latest")
        block_timestamp = block_info.get("timestamp")
        if not block_timestamp:
            raise ValueError("Block timestamp not found")
        return int(block_timestamp) & 0xFFFFFFFF

    @staticmethod
    def deserialize_callback(twapStruct: TWAP_STRUCT_TYPE, salt: HexStr) -> "Twap":
        return Twap(TWAP_ADDRESS, static_transform_tuple_to_data(twapStruct), salt)

    def to_string(self, token_formatter=None) -> str:
        data = self.data
        start_time = (
            "AT_MINING_TIME"
            if data.start_type == StartType.AT_MINING_TIME.value
            else data.start_time_epoch
        )
        duration_of_part = (
            "AUTO"
            if data.duration_type == DurationType.AUTO.value
            else data.duration_of_part
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

        return f"{self.order_type} ({self.id}): {json.dumps(details)}"

    def transform_data_to_struct(self, params: TwapData) -> TwapStruct:
        sell_amount = Decimal(params.sell_amount)
        buy_amount = Decimal(params.buy_amount)
        number_of_parts = Decimal(params.number_of_parts)

        part_sell_amount = sell_amount // number_of_parts if number_of_parts > 0 else 0
        min_part_limit = buy_amount // number_of_parts if number_of_parts > 0 else 0

        span = (
            0
            if params.duration_type == DurationType.AUTO.value
            else params.duration_of_part
        )
        t0 = (
            0
            if params.start_type == StartType.AT_MINING_TIME.value
            else params.start_time_epoch
        )

        return TwapStruct(
            sell_token=params.sell_token,
            buy_token=params.buy_token,
            receiver=params.receiver,
            part_sell_amount=int(part_sell_amount),
            min_part_limit=int(min_part_limit),
            t0=int(t0),
            n=int(params.number_of_parts),
            t=int(params.time_between_parts),
            span=int(span),
            app_data=params.app_data,
        )

    def transform_struct_to_data(self, params: TwapStruct) -> TwapData:
        return static_transform_struct_to_data(params)

    async def poll_validate(self, params: PollParams) -> Optional[PollResultError]:
        block_timestamp = await self.get_block_timestamp(params)
        print(block_timestamp)

        try:
            start_timestamp = await self.start_timestamp(params)

            if start_timestamp > block_timestamp:
                return PollResultError(
                    result=PollResultCode.TRY_AT_EPOCH,
                    epoch=start_timestamp,
                    reason=f"TWAP hasn't started yet. Starts at {start_timestamp} ({format_epoch(start_timestamp)})",
                )

            expiration_timestamp = self.end_timestamp(start_timestamp)
            if block_timestamp >= expiration_timestamp:
                return PollResultError(
                    result=PollResultCode.DONT_TRY_AGAIN,
                    reason=f"TWAP has expired. Expired at {expiration_timestamp} ({format_epoch(expiration_timestamp)})",
                )

            return None
        except Exception as err:
            if "Cabinet is not set" in str(err):
                return PollResultError(
                    result=PollResultCode.DONT_TRY_AGAIN,
                    reason=f"${str(err)}. User likely removed the order.",
                    error=err,
                )

            elif "Cabinet epoch out of range" in str(err):
                return PollResultError(
                    result=PollResultCode.DONT_TRY_AGAIN, reason=str(err)
                )

            return PollResultError(
                result=PollResultCode.UNEXPECTED_ERROR,
                reason=f"Unexpected error: {str(err)}",
                error=err,
            )

    async def start_timestamp(self, params: PollParams) -> int:
        start_type = self.data.start_type

        if start_type == StartType.AT_EPOCH.value:
            return self.data.start_time_epoch

        cabinet = await self.cabinet(params)
        raw_cabinet_epoch = Web3.to_int(hexstr=HexStr("0x" + cabinet))

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
        duration_type = self.data.duration_type
        duration_of_part = self.data.duration_of_part

        if duration_type == DurationType.LIMIT_DURATION.value:
            return (
                start_timestamp
                + (number_of_parts - 1) * time_between_parts
                + duration_of_part
            )

        return start_timestamp + number_of_parts * time_between_parts

    async def handle_poll_failed_already_present(
        self, order_uid: str, order: Order, params: PollParams
    ) -> Optional[PollResultError]:
        block_timestamp = await self.get_block_timestamp(params)
        time_between_parts = self.data.time_between_parts
        number_of_parts = self.data.number_of_parts
        start_timestamp = await self.start_timestamp(params)

        if block_timestamp < start_timestamp:
            return PollResultError(
                result=PollResultCode.UNEXPECTED_ERROR,
                reason=f"TWAP hasn't started yet. Starts at {start_timestamp} ({format_epoch(start_timestamp)})",
            )

        expire_time = number_of_parts * time_between_parts + start_timestamp
        if block_timestamp >= expire_time:
            return PollResultError(
                result=PollResultCode.UNEXPECTED_ERROR,
                reason=f"TWAP is expired. Expired at {expire_time} ({format_epoch(expire_time)})",
            )

        current_part_number = (block_timestamp - start_timestamp) // time_between_parts

        if current_part_number == number_of_parts - 1:
            return PollResultError(
                result=PollResultCode.DONT_TRY_AGAIN,
                reason=f"Current active TWAP part ({current_part_number + 1}/{number_of_parts}) is already in the Order Book. This was the last TWAP part, no more orders need to be placed",
            )

        next_part_start_time = (
            start_timestamp + (current_part_number + 1) * time_between_parts
        )

        return PollResultError(
            result=PollResultCode.TRY_AT_EPOCH,
            epoch=next_part_start_time,
            reason=f"Current active TWAP part ({current_part_number + 1}/{number_of_parts}) is already in the Order Book. TWAP part {current_part_number + 2} doesn't start until {next_part_start_time} ({format_epoch(next_part_start_time)})",
        )


def static_transform_tuple_to_struct(
    params: Tuple[str, str, str, int, int, int, int, int, int, bytes],
) -> TwapStruct:
    return TwapStruct(
        sell_token=params[0],
        buy_token=params[1],
        receiver=params[2],
        part_sell_amount=params[3],
        min_part_limit=params[4],
        t0=params[5],
        n=params[6],
        t=params[7],
        span=params[8],
        app_data=Web3.to_hex(params[9]),
    )


def static_transform_struct_to_data(
    params: TwapStruct,
) -> TwapData:
    duration_of_part = (
        {"type": DurationType.AUTO.value, "duration": 0}
        if params.span == 0
        else {
            "type": DurationType.LIMIT_DURATION.value,
            "duration": params.span,
        }
    )

    start_time = (
        {"type": StartType.AT_MINING_TIME.value, "epoch": 0}
        if params.t0 == 0
        else {"type": StartType.AT_EPOCH.value, "epoch": params.t0}
    )

    return TwapData(
        sell_token=params.sell_token,
        buy_token=params.buy_token,
        receiver=params.receiver,
        sell_amount=params.part_sell_amount * params.n,
        buy_amount=params.min_part_limit * params.n,
        number_of_parts=params.n,
        time_between_parts=params.t,
        app_data=params.app_data,
        duration_of_part=duration_of_part["duration"],
        start_type=start_time["type"],
        duration_type=duration_of_part["type"],
        start_time_epoch=start_time["epoch"],
    )


def static_transform_tuple_to_data(
    params: Tuple[str, str, str, int, int, int, int, int, int, bytes],
) -> TwapData:
    return static_transform_struct_to_data(static_transform_tuple_to_struct(params))
