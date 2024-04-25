import json
from typing import Any, Dict, List

from cow_py.common.api.api_base import ApiBase, Context
from cow_py.common.config import SupportedChainId
from cow_py.order_book.config import OrderBookAPIConfigFactory
from typing import Union
from cow_py.order_book.generated.model import OrderQuoteSide2, OrderQuoteValidity2

from .generated.model import (
    UID,
    Address,
    AppDataHash,
    AppDataObject,
    NativePriceResponse,
    Order,
    OrderCancellation,
    OrderCreation,
    OrderQuoteRequest,
    OrderQuoteResponse,
    OrderQuoteSide,
    OrderQuoteSide1,
    OrderQuoteSide3,
    OrderQuoteValidity,
    OrderQuoteValidity1,
    SolverCompetitionResponse,
    TotalSurplus,
    Trade,
    TransactionHash,
)


class OrderBookApi(ApiBase):
    def __init__(
        self,
        config=OrderBookAPIConfigFactory.get_config("prod", SupportedChainId.MAINNET),
    ):
        self.config = config

    async def get_version(self, context_override: Context = {}) -> str:
        return await self._fetch(
            path="/api/v1/version", context_override=context_override
        )

    async def get_trades_by_owner(
        self, owner: Address, context_override: Context = {}
    ) -> List[Trade]:
        response = await self._fetch(
            path="/api/v1/trades",
            params={"owner": owner},
            context_override=context_override,
        )
        return [Trade(**trade) for trade in response]

    async def get_trades_by_order_uid(
        self, order_uid: UID, context_override: Context = {}
    ) -> List[Trade]:
        response = await self._fetch(
            path="/api/v1/trades",
            params={"order_uid": order_uid},
            context_override=context_override,
        )
        return [Trade(**trade) for trade in response]

    async def get_orders_by_owner(
        self,
        owner: Address,
        limit: int = 1000,
        offset: int = 0,
        context_override: Context = {},
    ) -> List[Order]:
        return [
            Order(**order)
            for order in await self._fetch(
                path=f"/api/v1/account/{owner}/orders",
                params={"limit": limit, "offset": offset},
                context_override=context_override,
            )
        ]

    async def get_order_by_uid(
        self, order_uid: UID, context_override: Context = {}
    ) -> Order:
        response = await self._fetch(
            path=f"/api/v1/orders/{order_uid}",
            context_override=context_override,
        )
        return Order(**response)

    def get_order_link(self, order_uid: UID) -> str:
        return self.config.get_base_url() + f"/api/v1/orders/{order_uid.root}"

    async def get_tx_orders(
        self, tx_hash: TransactionHash, context_override: Context = {}
    ) -> List[Order]:
        response = await self._fetch(
            path=f"/api/v1/transactions/{tx_hash}/orders",
            context_override=context_override,
        )
        return [Order(**order) for order in response]

    async def get_native_price(
        self, tokenAddress: Address, context_override: Context = {}
    ) -> NativePriceResponse:
        response = await self._fetch(
            path=f"/api/v1/token/{tokenAddress}/native_price",
            context_override=context_override,
        )
        return NativePriceResponse(**response)

    async def get_total_surplus(
        self, user: Address, context_override: Context = {}
    ) -> TotalSurplus:
        response = await self._fetch(
            path=f"/api/v1/users/{user}/total_surplus",
            context_override=context_override,
        )
        return TotalSurplus(**response)

    async def get_app_data(
        self, app_data_hash: AppDataHash, context_override: Context = {}
    ) -> Dict[str, Any]:
        return await self._fetch(
            path=f"/api/v1/app_data/{app_data_hash}",
            context_override=context_override,
        )

    async def get_solver_competition(
        self, action_id: Union[int, str] = "latest", context_override: Context = {}
    ) -> SolverCompetitionResponse:
        response = await self._fetch(
            path=f"/api/v1/solver_competition/{action_id}",
            context_override=context_override,
        )
        return SolverCompetitionResponse(**response)

    async def get_solver_competition_by_tx_hash(
        self, tx_hash: TransactionHash, context_override: Context = {}
    ) -> SolverCompetitionResponse:
        response = await self._fetch(
            path=f"/api/v1/solver_competition/by_tx_hash/{tx_hash}",
            context_override=context_override,
        )
        return SolverCompetitionResponse(**response)

    async def post_quote(
        self,
        request: OrderQuoteRequest,
        side: Union[OrderQuoteSide, OrderQuoteSide1, OrderQuoteSide2, OrderQuoteSide3],
        validity: Union[
            OrderQuoteValidity, OrderQuoteValidity1, OrderQuoteValidity2
        ] = OrderQuoteValidity1(validTo=None),
        context_override: Context = {},
    ) -> OrderQuoteResponse:
        response = await self._fetch(
            path="/api/v1/quote",
            json={
                **request.model_dump(by_alias=True),
                # side object need to be converted to json first to avoid on kind type
                **json.loads(side.model_dump_json()),
                **validity.model_dump(),
            },
            context_override=context_override,
            method="POST",
        )
        return OrderQuoteResponse(**response)

    async def post_order(self, order: OrderCreation, context_override: Context = {}):
        response = await self._fetch(
            path="/api/v1/orders",
            json=json.loads(order.model_dump_json(by_alias=True)),
            context_override=context_override,
            method="POST",
        )
        return UID(response)

    async def delete_order(
        self,
        orders_cancelation: OrderCancellation,
        context_override: Context = {},
    ):
        response = await self._fetch(
            path="/api/v1/orders",
            json=orders_cancelation.model_dump_json(),
            context_override=context_override,
            method="DELETE",
        )
        return UID(response)

    async def put_app_data(
        self,
        app_data: AppDataObject,
        app_data_hash: str = "",
        context_override: Context = {},
    ) -> AppDataHash:
        app_data_hash_url = app_data_hash if app_data_hash else ""
        response = await self._fetch(
            path=f"/api/v1/app_data/{app_data_hash_url}",
            json=app_data.model_dump_json(),
            context_override=context_override,
            method="PUT",
        )
        return AppDataHash(response)
