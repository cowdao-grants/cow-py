from abc import ABC
from typing import Any, Optional

import httpx

from cow_py.common.api.decorators import rate_limitted, with_backoff
from cow_py.common.config import SupportedChainId

Context = dict[str, Any]


class APIConfig(ABC):
    """Base class for API configuration with common functionality."""

    config_map = {}

    def __init__(
        self, chain_id: SupportedChainId, base_context: Optional[Context] = None
    ):
        self.chain_id = chain_id
        self.context = base_context or {}

    def get_base_url(self) -> str:
        return self.config_map.get(
            self.chain_id, "default URL if chain_id is not found"
        )

    def get_context(self) -> Context:
        return {"base_url": self.get_base_url(), **self.context}


class RequestStrategy:
    async def make_request(self, client, url, method, **request_kwargs):
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
        }

        return await client.request(
            url=url, headers=headers, method=method, **request_kwargs
        )


class ResponseAdapter:
    async def adapt_response(self, _response):
        raise NotImplementedError()


class RequestBuilder:
    def __init__(self, strategy, response_adapter):
        self.strategy = strategy
        self.response_adapter = response_adapter

    async def execute(self, client, url, method, **kwargs):
        response = await self.strategy.make_request(client, url, method, **kwargs)
        return self.response_adapter.adapt_response(response)


class JsonResponseAdapter(ResponseAdapter):
    def adapt_response(self, response):
        if response.headers.get("content-type") == "application/json":
            return response.json()
        else:
            return response.text


class ApiBase:
    """Base class for APIs utilizing configuration and request execution."""

    def __init__(self, config: APIConfig):
        self.config = config

    @with_backoff()
    @rate_limitted()
    async def _fetch(self, path, method="GET", **kwargs):
        url = self.config.get_base_url() + path

        del kwargs["context_override"]

        async with httpx.AsyncClient() as client:
            builder = RequestBuilder(
                RequestStrategy(),
                JsonResponseAdapter(),
            )
            return await builder.execute(client, url, method, **kwargs)
