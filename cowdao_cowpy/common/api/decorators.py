import backoff
import httpx
from aiolimiter import AsyncLimiter

from cowdao_cowpy.common.api.errors import NetworkError, UnexpectedResponseError

DEFAULT_LIMITER_OPTIONS = {"rate": 5, "per": 1.0}

DEFAULT_BACKOFF_OPTIONS = {
    "max_tries": 10,
    "max_time": None,
    "jitter": None,
    # Forwarded to backoff.expo: caps each wait so total backoff stays bounded.
    "max_value": 8,
}

# HTTP statuses that are worth retrying, mirroring the TS SDK behavior.
RETRYABLE_STATUS_CODES = frozenset({408, 425, 429, 500, 502, 503, 504})

RETRYABLE_EXCEPTIONS = (httpx.TransportError, httpx.HTTPStatusError, NetworkError)


def is_retryable(exception: Exception) -> bool:
    """Return True when the exception represents a transient failure worth retrying."""
    if isinstance(exception, httpx.HTTPStatusError):
        return exception.response.status_code in RETRYABLE_STATUS_CODES
    return isinstance(exception, (httpx.TransportError, NetworkError))


def dig(self, *keys):
    try:
        for key in keys:
            self = self[key]
        return self
    except KeyError:
        return None


def with_backoff():
    def decorator(func):
        async def wrapper(*args, **kwargs):
            backoff_opts = dig(kwargs, "context_override", "backoff_opts")

            # Merge so partial overrides (e.g. {"max_tries": 3}) keep the
            # remaining defaults, notably the max_value wait cap.
            internal_backoff_opts = {**DEFAULT_BACKOFF_OPTIONS, **(backoff_opts or {})}

            @backoff.on_exception(
                backoff.expo,
                RETRYABLE_EXCEPTIONS,
                giveup=lambda e: not is_retryable(e),
                **internal_backoff_opts,
            )
            async def closure():
                return await func(*args, **kwargs)

            try:
                return await closure()
            except httpx.HTTPStatusError as e:
                if is_retryable(e):
                    # Retries exhausted on a retryable status: surface the same
                    # typed error callers historically received.
                    raise UnexpectedResponseError(
                        f"HTTP error {e.response.status_code} persisted after retries: {e.response.text}",
                        e.response,
                    ) from e
                raise

        return wrapper

    return decorator


def rate_limitted(
    rate=DEFAULT_LIMITER_OPTIONS["rate"], per=DEFAULT_LIMITER_OPTIONS["per"]
):
    def decorator(func):
        limiter = AsyncLimiter(rate, per)

        async def wrapper(*args, **kwargs):
            async with limiter:
                return await func(*args, **kwargs)

        return wrapper

    return decorator
