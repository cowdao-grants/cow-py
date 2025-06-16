from abc import ABC
import json
from typing import Any, Dict, List, Literal, Optional, Type, TypeVar, Union, get_args

import httpx

from cowdao_cowpy.common.api.decorators import rate_limitted, with_backoff
from cowdao_cowpy.common.api.errors import (
    ApiResponseError,
    NetworkError,
    SerializationError,
    UnexpectedResponseError,
)
from cowdao_cowpy.common.config import SupportedChainId

from cowdao_cowpy.order_book.generated.model import BaseModel

Envs = Literal["prod", "staging"]

T = TypeVar("T")
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
        base_url = self.config_map.get(
            self.chain_id,
        )
        if not base_url:
            raise ValueError(
                f"No base URL configured for chain ID {self.chain_id}. "
                "Please ensure the configuration is set up correctly."
            )
        return base_url

    def get_context(self) -> Context:
        return {"base_url": self.get_base_url(), **self.context}

    def with_env(self, env: Envs) -> "APIConfig":
        """
        Create a new config instance for the specified environment.
        The default implementation just returns self.

        Args:
            env: The environment to switch to

        Returns:
            A new APIConfig instance for the specified environment
        """
        return self


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
    def adapt_response(self, _response) -> Dict[str, Any] | str:
        raise NotImplementedError()


class RequestBuilder:
    def __init__(self, strategy, response_adapter):
        self.strategy = strategy
        self.response_adapter = response_adapter

    async def execute(self, client, url, method, **kwargs):
        response = await self.strategy.make_request(client, url, method, **kwargs)
        return self.response_adapter.adapt_response(response)


class JsonResponseAdapter(ResponseAdapter):
    def adapt_response(self, response: httpx.Response) -> Dict[str, Any] | str:
        try:
            response.raise_for_status()
            if response.headers.get("content-type") == "application/json":
                return response.json()
            else:
                return response.text
        except json.JSONDecodeError as e:
            raise SerializationError(
                f"Failed to decode JSON response: {str(e)}", response.text
            )
        except httpx.HTTPStatusError as e:
            raise ApiResponseError(
                f"HTTP error {e.response.status_code}: {e.response.text}",
                str(e.response.status_code),
                e.response,
            )


class ApiBase:
    def __init__(self, config: APIConfig):
        self.config = config
        self.request_strategy = RequestStrategy()
        self.response_adapter = JsonResponseAdapter()
        self.request_builder = RequestBuilder(
            self.request_strategy, self.response_adapter
        )

    @staticmethod
    def serialize_model(data: Union[BaseModel, Dict[str, Any]]) -> Dict[str, Any]:
        if isinstance(data, BaseModel):
            return json.loads(data.model_dump_json(by_alias=True))
        elif isinstance(data, dict):
            return data
        else:
            raise ValueError(f"Unsupported type for serialization: {type(data)}")

    @staticmethod
    def deserialize_model(
        data: Union[Dict[str, Any], List[Dict[str, Any]], str], model_class: Type[T]
    ) -> Union[T, List[T]]:
        if isinstance(data, str):
            return model_class(data)  # type: ignore
        if isinstance(data, list):
            model_class, *_ = get_args(model_class)
            errors = []
            results = []
            for item in data:
                try:
                    results.append(model_class(**item))
                except Exception as e:
                    errors.append((item, str(e)))
            if errors:
                raise ValueError(f"Failed to deserialize some items: {errors}")
            return results
        if isinstance(data, dict):
            return model_class(**data)
        raise ValueError(f"Unsupported data type for deserialization: {type(data)}")

    @with_backoff()
    @rate_limitted()
    async def _fetch(
        self,
        path: str,
        method: str = "GET",
        response_model: Optional[Type[T]] = None,
        **kwargs,
    ) -> Union[T, Any]:
        """
        Makes an API request with backoff and rate limiting applied.

        Args:
            path: The API endpoint path to request
            method: HTTP method to use (GET, POST, etc.)
            response_model: Optional Pydantic model to deserialize the response into
            **kwargs: Additional arguments to pass to the HTTP client
                - context_override: Dict with request-specific configuration:
                    - env: Override the environment for this request ("prod", "staging")
                    - backoff_opts: Custom backoff options
                    - Any other httpx client parameters

        Returns:
            The API response, deserialized into response_model if provided
        """
        context_override = kwargs.get("context_override", {})
        url_override = None

        # Handle environment override
        if "env" in context_override:
            env = context_override.pop("env")  # Remove to avoid passing to httpx
            try:
                # Use the config's with_env method to get a config for the desired environment
                temp_config = self.config.with_env(env)
                url_override = temp_config.get_base_url() + path
            except Exception as e:
                # Log the error but continue with the default URL
                print(f"Error switching environment: {e}")

        # Use the overridden URL or the default one
        url = url_override or self.config.get_base_url() + path

        kwargs = {k: v for k, v in kwargs.items() if k != "context_override"}

        if "json" in kwargs:
            kwargs["json"] = self.serialize_model(kwargs["json"])

        try:
            async with httpx.AsyncClient() as client:
                data = await self.request_builder.execute(client, url, method, **kwargs)
                if isinstance(data, dict) and "errorType" in data:
                    raise ApiResponseError(
                        f"API returned an error: {data.get('description', 'No description')}",
                        data["errorType"],
                        data,
                    )

                return (
                    self.deserialize_model(data, response_model)
                    if response_model
                    else data
                )

        except httpx.NetworkError as e:
            raise NetworkError(f"Network error occurred: {str(e)}")
        except httpx.HTTPStatusError as e:
            if e.response.status_code in (429, 500):
                raise e
            raise ApiResponseError(
                f"HTTP error {e.response.status_code}: {e.response.text}",
                str(e.response.status_code),
                e.response,
            )
        except json.JSONDecodeError as e:
            raise SerializationError(f"Failed to decode JSON response: {str(e)}")
        except Exception as e:
            raise UnexpectedResponseError(f"An unexpected error occurred: {str(e)}")
