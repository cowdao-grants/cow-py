from abc import ABC
import asyncio
import importlib.metadata
import json
from typing import Any, Dict, List, Literal, Optional, Type, TypeVar, Union, get_args

import httpx

from cowdao_cowpy.common.api.decorators import (
    RETRYABLE_STATUS_CODES,
    rate_limitted,
    with_backoff,
)
from cowdao_cowpy.common.api.errors import (
    ApiResponseError,
    BaseApiError,
    NetworkError,
    SerializationError,
    UnexpectedResponseError,
)
from cowdao_cowpy.common.config import SupportedChainId

from cowdao_cowpy.order_book.generated.model import BaseModel

Envs = Literal["prod", "staging"]

T = TypeVar("T")
Context = dict[str, Any]

try:
    _VERSION = importlib.metadata.version("cowdao-cowpy")
except importlib.metadata.PackageNotFoundError:
    _VERSION = "development"

USER_AGENT = f"cowdao-cowpy/{_VERSION}"


class APIConfig(ABC):
    """Base class for API configuration with common functionality."""

    config_map: Dict[SupportedChainId, str] = {}
    partner_config_map: Dict[SupportedChainId, str] = {}

    def __init__(
        self,
        chain_id: SupportedChainId,
        base_context: Optional[Context] = None,
        bearer_token: Optional[str] = None,
        api_key: Optional[str] = None,
    ):
        self.chain_id = chain_id
        self.context = dict(base_context) if base_context else {}
        if bearer_token is not None:
            self.context["bearer_token"] = bearer_token
        if api_key is not None:
            self.context["api_key"] = api_key

    @property
    def bearer_token(self) -> Optional[str]:
        return self.context.get("bearer_token")

    @property
    def api_key(self) -> Optional[str]:
        return self.context.get("api_key")

    def get_base_url(self, api_key: Optional[str] = None) -> str:
        effective_api_key = api_key if api_key is not None else self.api_key
        if effective_api_key:
            partner_base_url = self.partner_config_map.get(self.chain_id)
            if partner_base_url:
                return partner_base_url
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
    async def make_request(
        self,
        client: httpx.AsyncClient,
        url: str,
        method: str,
        headers: Optional[Dict[str, str]] = None,
        **request_kwargs,
    ):
        merged_headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "user-agent": USER_AGENT,
        }
        if headers:
            merged_headers.update({k.lower(): v for k, v in headers.items()})

        return await client.request(
            url=url, headers=merged_headers, method=method, **request_kwargs
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


def _extract_error_type(response: httpx.Response) -> str:
    """Pull the orderbook errorType out of an error response body when available."""
    try:
        body = response.json()
        if isinstance(body, dict) and "errorType" in body:
            return str(body["errorType"])
    except Exception:
        pass
    return str(response.status_code)


class ApiBase:
    def __init__(self, config: APIConfig, client: Optional[httpx.AsyncClient] = None):
        self.config = config
        self.request_strategy = RequestStrategy()
        self.response_adapter = JsonResponseAdapter()
        self.request_builder = RequestBuilder(
            self.request_strategy, self.response_adapter
        )
        self._injected_client = client
        self._client: Optional[httpx.AsyncClient] = None
        self._client_loop: Optional[asyncio.AbstractEventLoop] = None

    def _get_client(self) -> httpx.AsyncClient:
        """Return the HTTP client to use, creating (and reusing) one if none was injected.

        A lazily created client is bound to the running event loop; if the loop
        changes (e.g. successive asyncio.run() calls), a fresh client is created.
        """
        if self._injected_client is not None:
            return self._injected_client

        loop = asyncio.get_running_loop()
        if (
            self._client is None
            or self._client.is_closed
            or self._client_loop is not loop
        ):
            if self._client is not None and not self._client.is_closed:
                # The old client is bound to another loop, so it cannot be
                # closed here. Close it on its own loop if that loop is still
                # alive; with asyncio.run()-per-call the old loop is already
                # closed and its transports were torn down with it.
                old_client, old_loop = self._client, self._client_loop
                if old_loop is not None and not old_loop.is_closed():
                    asyncio.run_coroutine_threadsafe(old_client.aclose(), old_loop)
            self._client = httpx.AsyncClient()
            self._client_loop = loop
        return self._client

    async def aclose(self) -> None:
        """Close the lazily created HTTP client. Injected clients are managed by the caller."""
        if self._client is not None and not self._client.is_closed:
            await self._client.aclose()

    def _build_auth_headers(self, context_override: Context) -> Dict[str, str]:
        headers: Dict[str, str] = {}
        bearer_token = context_override.get("bearer_token", self.config.bearer_token)
        api_key = context_override.get("api_key", self.config.api_key)
        if bearer_token:
            headers["Authorization"] = f"Bearer {bearer_token}"
        if api_key:
            headers["X-API-Key"] = api_key
        return headers

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
                    - bearer_token: Request-specific Authorization bearer token
                    - api_key: Request-specific X-API-Key header
                    - Any other httpx client parameters

        Returns:
            The API response, deserialized into response_model if provided
        """
        context_override = kwargs.get("context_override", {})
        url_override = None
        # A request-scoped api_key must also affect URL routing (partner
        # gateway), not just the X-API-Key header.
        api_key_override = context_override.get("api_key")

        # Handle environment override
        if "env" in context_override:
            env = context_override.pop("env")  # Remove to avoid passing to httpx
            try:
                # Use the config's with_env method to get a config for the desired environment
                temp_config = self.config.with_env(env)
                url_override = temp_config.get_base_url(api_key=api_key_override) + path
            except Exception as e:
                # Log the error but continue with the default URL
                print(f"Error switching environment: {e}")

        # Use the overridden URL or the default one
        url = url_override or self.config.get_base_url(api_key=api_key_override) + path

        kwargs = {k: v for k, v in kwargs.items() if k != "context_override"}

        headers = {
            **self._build_auth_headers(context_override),
            **(kwargs.pop("headers", None) or {}),
        }
        if headers:
            kwargs["headers"] = headers

        if "json" in kwargs:
            kwargs["json"] = self.serialize_model(kwargs["json"])

        try:
            client = self._get_client()
            data = await self.request_builder.execute(client, url, method, **kwargs)
            if isinstance(data, dict) and "errorType" in data:
                raise ApiResponseError(
                    f"API returned an error: {data.get('description', 'No description')}",
                    data["errorType"],
                    data,
                )

            return (
                self.deserialize_model(data, response_model) if response_model else data
            )

        except httpx.TransportError as e:
            raise NetworkError(f"Network error occurred: {str(e)}") from e
        except httpx.HTTPStatusError as e:
            if e.response.status_code in RETRYABLE_STATUS_CODES:
                raise
            raise ApiResponseError(
                f"HTTP error {e.response.status_code}: {e.response.text}",
                _extract_error_type(e.response),
                e.response,
            ) from e
        except json.JSONDecodeError as e:
            raise SerializationError(f"Failed to decode JSON response: {str(e)}")
        except BaseApiError:
            raise
        except Exception as e:
            raise UnexpectedResponseError(f"An unexpected error occurred: {str(e)}")
