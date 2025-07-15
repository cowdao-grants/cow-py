import importlib.metadata

try:
    __version__ = importlib.metadata.version("cowdao-cowpy")
except importlib.metadata.PackageNotFoundError:
    __version__ = "development"

from cowdao_cowpy.cow.swap import swap_tokens

__all__ = ["swap_tokens", "__version__"]
