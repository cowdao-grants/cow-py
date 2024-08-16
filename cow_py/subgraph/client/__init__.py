# Generated by ariadne-codegen

from .async_base_client import AsyncBaseClient
from .base_model import BaseModel, Upload
from .enums import (
    Aggregation_interval,
    Bundle_orderBy,
    DailyTotal_orderBy,
    HourlyTotal_orderBy,
    Order_orderBy,
    OrderDirection,
    Pair_orderBy,
    PairDaily_orderBy,
    PairHourly_orderBy,
    Settlement_orderBy,
    Token_orderBy,
    TokenDailyTotal_orderBy,
    TokenHourlyTotal_orderBy,
    TokenTradingEvent_orderBy,
    Total_orderBy,
    Trade_orderBy,
    UniswapPool_orderBy,
    UniswapToken_orderBy,
    User_orderBy,
    _SubgraphErrorPolicy_,
)
from .exceptions import (
    GraphQLClientError,
    GraphQLClientGraphQLError,
    GraphQLClientGraphQLMultiError,
    GraphQLClientHttpError,
    GraphQLClientInvalidResponseError,
)
from .input_types import (
    Block_height,
    BlockChangedFilter,
    Bundle_filter,
    DailyTotal_filter,
    HourlyTotal_filter,
    Order_filter,
    Pair_filter,
    PairDaily_filter,
    PairHourly_filter,
    Settlement_filter,
    Token_filter,
    TokenDailyTotal_filter,
    TokenHourlyTotal_filter,
    TokenTradingEvent_filter,
    Total_filter,
    Trade_filter,
    UniswapPool_filter,
    UniswapToken_filter,
    User_filter,
)
from .last_days_volume import LastDaysVolume, LastDaysVolumeDailyTotals
from .last_hours_volume import LastHoursVolume, LastHoursVolumeHourlyTotals
from .subgraph_client import SubgraphClient
from .totals import Totals, TotalsTotals

__all__ = [
    "Aggregation_interval",
    "AsyncBaseClient",
    "BaseModel",
    "BlockChangedFilter",
    "Block_height",
    "Bundle_filter",
    "Bundle_orderBy",
    "DailyTotal_filter",
    "DailyTotal_orderBy",
    "GraphQLClientError",
    "GraphQLClientGraphQLError",
    "GraphQLClientGraphQLMultiError",
    "GraphQLClientHttpError",
    "GraphQLClientInvalidResponseError",
    "HourlyTotal_filter",
    "HourlyTotal_orderBy",
    "LastDaysVolume",
    "LastDaysVolumeDailyTotals",
    "LastHoursVolume",
    "LastHoursVolumeHourlyTotals",
    "OrderDirection",
    "Order_filter",
    "Order_orderBy",
    "PairDaily_filter",
    "PairDaily_orderBy",
    "PairHourly_filter",
    "PairHourly_orderBy",
    "Pair_filter",
    "Pair_orderBy",
    "Settlement_filter",
    "Settlement_orderBy",
    "SubgraphClient",
    "TokenDailyTotal_filter",
    "TokenDailyTotal_orderBy",
    "TokenHourlyTotal_filter",
    "TokenHourlyTotal_orderBy",
    "TokenTradingEvent_filter",
    "TokenTradingEvent_orderBy",
    "Token_filter",
    "Token_orderBy",
    "Total_filter",
    "Total_orderBy",
    "Totals",
    "TotalsTotals",
    "Trade_filter",
    "Trade_orderBy",
    "UniswapPool_filter",
    "UniswapPool_orderBy",
    "UniswapToken_filter",
    "UniswapToken_orderBy",
    "Upload",
    "User_filter",
    "User_orderBy",
    "_SubgraphErrorPolicy_",
]