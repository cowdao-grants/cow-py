from typing import Any, Dict, List, Optional, Union

import httpx

from cowdao_cowpy.common.api.api_base import ApiBase, Context
from cowdao_cowpy.common.api.errors import UnexpectedResponseError
from cowdao_cowpy.common.config import SupportedChainId, ENVS_LIST
from cowdao_cowpy.order_book.config import OrderBookAPIConfigFactory
from cowdao_cowpy.order_book.generated.model import (
    UID,
    Address,
    AppDataHash,
    AppDataObject,
    CompetitionOrderStatus,
    NativePriceResponse,
    Order,
    OrderCreation,
    OrderQuoteRequest,
    OrderQuoteResponse,
    OrderQuoteSide,
    OrderQuoteSide1,
    OrderQuoteSide2,
    OrderQuoteSide3,
    OrderQuoteValidity,
    OrderQuoteValidity1,
    OrderQuoteValidity2,
    SolverCompetitionResponse,
    TotalSurplus,
    Trade,
    TransactionHash,
    OrderCancellations,
)


class OrderBookApi(ApiBase):
    def __init__(
        self,
        config=OrderBookAPIConfigFactory.get_config("prod", SupportedChainId.MAINNET),
        client: Optional[httpx.AsyncClient] = None,
    ):
        super().__init__(config, client=client)

    async def get_version(self, context_override: Context = {}) -> str:
        return await self._fetch("/api/v1/version", context_override=context_override)

    async def get_trades_by_owner(
        self, owner: Address, context_override: Context = {}
    ) -> List[Trade]:
        response = await self._fetch(
            path="/api/v1/trades",
            params={"owner": owner},
            context_override=context_override,
            response_model=List[Trade],
        )
        return response

    async def get_trades_by_order_uid(
        self, order_uid: UID, context_override: Context = {}
    ) -> List[Trade]:
        response = await self._fetch(
            path="/api/v1/trades",
            params={"order_uid": order_uid},
            context_override=context_override,
            response_model=List[Trade],
        )
        return response

    async def get_orders_by_owner(
        self,
        owner: Address,
        limit: int = 1000,
        offset: int = 0,
        context_override: Context = {},
    ) -> List[Order]:
        return await self._fetch(
            path=f"/api/v1/account/{owner}/orders",
            params={"limit": limit, "offset": offset},
            context_override=context_override,
            response_model=List[Order],
        )

    async def get_order_by_uid(
        self, order_uid: UID, context_override: Context = {}
    ) -> Order:
        return await self._fetch(
            path=f"/api/v1/orders/{order_uid.root}",
            context_override=context_override,
            response_model=Order,
        )

    async def get_order_multi_env(
        self, order_uid: UID, context_override: Context = {}
    ) -> Order | None:
        for env in ENVS_LIST:
            # TODO extract & exclude current env from loop.
            try:
                result = await self.get_order_by_uid(
                    order_uid, {**context_override, "env": env.value}
                )
                return result
            except UnexpectedResponseError:
                pass

    async def get_order_competition_status(
        self, order_uid: UID, context_override: Context = {}
    ) -> CompetitionOrderStatus:
        return await self._fetch(
            path=f"/api/v1/orders/{order_uid.root}/status",
            context_override=context_override,
            response_model=CompetitionOrderStatus,
        )

    def get_order_link(self, order_uid: UID) -> str:
        return f"{self.config.get_base_url()}/api/v1/orders/{order_uid.root}"

    async def get_tx_orders(
        self, tx_hash: TransactionHash, context_override: Context = {}
    ) -> List[Order]:
        return await self._fetch(
            path=f"/api/v1/transactions/{tx_hash}/orders",
            context_override=context_override,
            response_model=List[Order],
        )

    async def get_native_price(
        self, token_address: Address, context_override: Context = {}
    ) -> NativePriceResponse:
        return await self._fetch(
            path=f"/api/v1/token/{token_address}/native_price",
            context_override=context_override,
            response_model=NativePriceResponse,
        )

    async def get_total_surplus(
        self, user: Address, context_override: Context = {}
    ) -> TotalSurplus:
        return await self._fetch(
            path=f"/api/v1/users/{user}/total_surplus",
            context_override=context_override,
            response_model=TotalSurplus,
        )

    async def get_solver_competition(
        self, action_id: Union[int, str] = "latest", context_override: Context = {}
    ) -> SolverCompetitionResponse:
        # v1 was decommissioned; v2 exposes a dedicated /latest path and keys
        # the by-id lookup on the auction id.
        path = (
            "/api/v2/solver_competition/latest"
            if action_id == "latest"
            else f"/api/v2/solver_competition/{action_id}"
        )
        return await self._fetch(
            path=path,
            context_override=context_override,
            response_model=SolverCompetitionResponse,
        )

    async def get_solver_competition_by_tx_hash(
        self, tx_hash: TransactionHash, context_override: Context = {}
    ) -> SolverCompetitionResponse:
        return await self._fetch(
            path=f"/api/v2/solver_competition/by_tx_hash/{tx_hash}",
            context_override=context_override,
            response_model=SolverCompetitionResponse,
        )

    async def post_quote(
        self,
        request: OrderQuoteRequest,
        side: Union[OrderQuoteSide, OrderQuoteSide1, OrderQuoteSide2, OrderQuoteSide3],
        validity: Union[
            OrderQuoteValidity, OrderQuoteValidity1, OrderQuoteValidity2
        ] = OrderQuoteValidity1(validTo=None),
        context_override: Context = {},
    ) -> OrderQuoteResponse:
        json_data = {
            **self.serialize_model(request),
            **self.serialize_model(side),  # type: ignore
            **self.serialize_model(validity),  # type: ignore
        }
        return await self._fetch(
            path="/api/v1/quote",
            method="POST",
            json=json_data,
            context_override=context_override,
            response_model=OrderQuoteResponse,
        )

    async def post_order(
        self, order: OrderCreation, context_override: Context = {}
    ) -> UID:
        response = await self._fetch(
            path="/api/v1/orders",
            method="POST",
            json=order,
            context_override=context_override,
        )
        return UID(response)

    async def delete_order(
        self, orders_cancelation: OrderCancellations, context_override: Context = {}
    ) -> str:
        return await self._fetch(
            path="/api/v1/orders",
            method="DELETE",
            json=orders_cancelation,
            context_override=context_override,
        )

    async def put_app_data(
        self,
        app_data: AppDataObject,
        app_data_hash: AppDataHash = None,
        context_override: Context = {},
    ) -> AppDataHash:
        # Interpolating the AppDataHash model directly would produce
        # "root='0x...'" in the URL; the API needs the bare hash string.
        if isinstance(app_data_hash, AppDataHash):
            app_data_hash_url = app_data_hash.root
        else:
            app_data_hash_url = app_data_hash or ""
        response = await self._fetch(
            path=f"/api/v1/app_data/{app_data_hash_url}",
            method="PUT",
            json=app_data,
            context_override=context_override,
            response_model=AppDataHash,
        )
        return response

    async def get_app_data(
        self, app_data_hash: AppDataHash, context_override: Context = {}
    ) -> Dict[str, Any]:
        return await self._fetch(
            path=f"/api/v1/app_data/{app_data_hash.root}",  #
            context_override=context_override,
        )
