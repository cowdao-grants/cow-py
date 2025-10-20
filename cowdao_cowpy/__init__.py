import importlib.metadata

import warnings


try:
    __version__ = importlib.metadata.version("cowdao-cowpy")
except importlib.metadata.PackageNotFoundError:
    __version__ = "development"
finally:
    warnings.filterwarnings(
        "ignore",
        category=UserWarning,
        module="pydantic.main",
        message=".*Pydantic serializer warnings.*",
    )


from cowdao_cowpy.cow.swap import swap_tokens, TokenSwapper
from cowdao_cowpy.common.chains import Chain


__all__ = ["swap_tokens", "TokenSwapper", "Chain", "__version__"]
