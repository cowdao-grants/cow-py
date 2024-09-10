import backoff
import httpx
from aiolimiter import AsyncLimiter

DEFAULT_LIMITER_OPTIONS = {"rate": 5, "per": 1.0}

DEFAULT_BACKOFF_OPTIONS = {
    "max_tries": 10,
    "max_time": None,
    "jitter": None,
}


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

            if backoff_opts is None:
                internal_backoff_opts = DEFAULT_BACKOFF_OPTIONS
            else:
                internal_backoff_opts = backoff_opts

            @backoff.on_exception(
                backoff.expo,
                (httpx.NetworkError, httpx.HTTPStatusError),
                **internal_backoff_opts,
            )
            async def closure():
                return await func(*args, **kwargs)

            return await closure()

        return wrapper

    return decorator


def rate_limitted(
    rate=DEFAULT_LIMITER_OPTIONS["rate"], per=DEFAULT_LIMITER_OPTIONS["per"]
):
    limiter = AsyncLimiter(rate, per)

    def decorator(func):
        async def wrapper(*args, **kwargs):
            async with limiter:
                return await func(*args, **kwargs)

        return wrapper

    return decorator
