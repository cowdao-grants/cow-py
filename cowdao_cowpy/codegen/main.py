import importlib.resources
import os

from cowdao_cowpy.codegen.abi_handler import ABIHandler
from cowdao_cowpy.contracts import abi


def get_all_abis():
    pkg_files = importlib.resources.files(abi)
    return [
        posix_path
        for posix_path in pkg_files.iterdir()
        if posix_path.suffix == ".json"  # type: ignore
    ]


def main():
    contracts_abis = get_all_abis()
    for abi_file_path in contracts_abis:
        contract_name = str(abi_file_path).split("/")[-1].split(".json")[0]
        handler = ABIHandler(contract_name, str(abi_file_path))

        content = handler.generate()

        base_path = os.path.dirname(os.path.abspath(__file__))

        os.makedirs(f"{base_path}/__generated__", exist_ok=True)
        generated = f"{base_path}/__generated__/{contract_name}.py"

        with open(generated, "w") as f:
            f.write(content)

    print("Done")


if __name__ == "__main__":
    main()
