from typing import Any, Dict, Optional

from httpx import Response


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

    def __init__(
        self, message: str, error_type: str, response: Dict[str, Any] | Response
    ):
        self.error_type = error_type
        super().__init__(message, response)


class NetworkError(BaseApiError):
    """Raised when there's a network-related error."""

    pass


class UnexpectedResponseError(BaseApiError):
    """Raised when the API returns an unexpected response."""

    pass
