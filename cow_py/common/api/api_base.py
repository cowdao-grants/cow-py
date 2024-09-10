from abc import ABC
import json
from typing import Any, Dict, Optional

import httpx

from cow_py.common.api.decorators import rate_limitted, with_backoff
from cow_py.common.config import SupportedChainId

Context = dict[str, Any]


class BaseApiError(Exception):
    """Base exception for OrderBookApi errors."""

    def __init__(self, message: str, response: Optional[Any] = None):
        self.message = message
        self.response = response
        super().__init__(self.message)


class SerializationError(BaseApiError):
    """Raised when there's an error in serializing or deserializing data."""

    pass


class ApiResponseError(BaseApiError):
    """Raised when the API returns an error response."""

    def __init__(self, message: str, error_type: str, response: Dict[str, Any]):
        self.error_type = error_type
        super().__init__(message, response)


class NetworkError(BaseApiError):
    """Raised when there's a network-related error."""

    pass


class UnexpectedResponseError(BaseApiError):
    """Raised when the API returns an unexpected response."""

    pass


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
    def adapt_response(self, response: httpx.Response) -> Any:
        try:
            if response.headers.get("content-type") == "application/json":
                return response.json()
            else:
                return response.text
        except json.JSONDecodeError as e:
            raise SerializationError(
                f"Failed to decode JSON response: {str(e)}", response.text
            )


class ApiBase:
    def __init__(self, config: APIConfig):
        self.config = config

    @with_backoff()
    @rate_limitted()
    async def _fetch(self, path: str, method="GET", **kwargs):
        url = self.config.get_base_url() + path
        del kwargs["context_override"]

        try:
            async with httpx.AsyncClient() as client:
                builder = RequestBuilder(RequestStrategy(), JsonResponseAdapter())
                response = await builder.execute(client, url, method, **kwargs)

                if isinstance(response, dict) and "errorType" in response:
                    raise ApiResponseError(
                        f"API returned an error: {response.get('description', 'No description')}",
                        response["errorType"],
                        response,
                    )

                return response
        except httpx.NetworkError as e:
            raise NetworkError(f"Network error occurred: {str(e)}")
        except httpx.HTTPStatusError as e:
            raise UnexpectedResponseError(
                f"Unexpected HTTP status: {e.response.status_code}", e.response
            )
        except Exception as e:
            raise BaseApiError(f"An unexpected error occurred: {str(e)}")
