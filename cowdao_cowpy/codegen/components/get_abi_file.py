import importlib.resources

from cowdao_cowpy.contracts import abi


def get_abi_file(contract_name: str) -> str:
    pkg_files = importlib.resources.files(abi)
    return str(
        next(
            x
            for x in pkg_files.iterdir()
            if x.suffix == ".json"  # type: ignore
            and x.name.split(".json")[0] == contract_name
        )
    )
