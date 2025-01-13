import importlib.resources
import re
from typing import Any, Dict, List

from pybars import Compiler

from cowdao_cowpy.codegen.components import templates
from cowdao_cowpy.codegen.components.abi_loader import FileAbiLoader
from cowdao_cowpy.codegen.components.templates import partials
from cowdao_cowpy.codegen.solidity_converter import SolidityConverter

CAMEL_TO_SNAKE_REGEX = re.compile(
    r"(?<=[a-z0-9])(?=[A-Z])|"  # Lowercase or digit to uppercase
    r"(?<=[A-Z])(?=[A-Z][a-z])|"  # Uppercase to uppercase followed by lowercase
    r"(?<=[A-Za-z])(?=[0-9])|"  # Letter to digit
    r"(?<=[0-9])(?=[A-Z])"  # Digit to uppercase
)


def compile_partial(partial_path: str) -> str:
    with open(partial_path, "r") as file:
        partial = file.read()
    compiler = Compiler()
    return compiler.compile(partial)


def get_filename_without_extension(path: str):
    """
    Returns the a filename from the path, without the extension.
    """
    return path.split("/")[-1].split(".")[0]


def to_python_conventional_name(name: str) -> str:
    """Converts a camelCase or PascalCase name to a snake_case name."""
    if name.isupper():
        return name.lower()

    return CAMEL_TO_SNAKE_REGEX.sub("_", name).lower()


def to_camel_case(name: str) -> str:
    """Converts a snake_case name to a camelCase name."""
    name = name.lower()
    return name[0] + name.title().replace("_", "")[1:]


def dict_keys_to_camel_case(d: Dict[str, Any]) -> Dict[str, Any]:
    """Converts all keys in a dictionary to camelCase."""
    return {to_camel_case(k): v for k, v in d.items()}


def _get_template_file() -> str:
    pkg_files = importlib.resources.files(templates)
    return str(next(x for x in pkg_files.iterdir() if x.suffix == ".hbs"))  # type: ignore


def _get_partials_files() -> str:
    pkg_files = importlib.resources.files(partials)
    return [str(x) for x in pkg_files.iterdir() if x.suffix == ".hbs"]  # type: ignore


class ABIHandlerError(Exception):
    """Raised when an error occurs in the ABI handler."""

    pass


class ABIHandler:
    """
    Handles the generation of Python classes and methods from Ethereum contract ABIs.

    This class reads the ABI of a contract, processes its contents, and generates Python code that mirrors
    the contract's functions and data structures.

    Attributes:
        contract_name (str): Name of the contract, used for generating class names.
        abi_file_path (str): Path to the ABI JSON file of the contract.

    Methods:
        generate: Main method to generate Python code from the ABI..
    """

    def __init__(self, contract_name: str, abi_file_path: str):
        self.contract_name = contract_name
        self.abi_file_path = abi_file_path

    def generate(self) -> str:
        """
        Generates Python code representing the contract's ABI.

        This method processes the ABI file, extracting information about functions,
        input/output arguments, enums, and data structures. It then uses this information
        to generate corresponding Python classes and methods.

        Returns:
            str: The generated Python code as a string.

        Raises:
            ABIHandlerError: If an error occurs during ABI processing or code generation.
        """
        try:
            template_data = self._prepare_template_data()
            return self._render_template(template_data)
        except Exception as e:
            raise ABIHandlerError(f"Error generating code: {str(e)}") from e

    def _prepare_template_data(self) -> Dict[str, Any]:
        """
        Prepares data for the template rendering based on the contract's ABI.

        This method processes the ABI to extract relevant information for generating
        Python code, such as methods, data classes, and enums.

        Returns:
            Dict[str, Any]: A dictionary containing the structured data for rendering.

        Raises:
            ABIHandlerError: If an error occurs during ABI processing.
        """
        try:
            methods, data_classes, enums = [], [], []
            generated_structs, generated_enums = set(), set()

            abi = FileAbiLoader(self.abi_file_path).load_abi()

            for item in abi:
                if item["type"] == "function":
                    methods.append(self._process_function(item))
                    for param in item["inputs"] + item.get("outputs", []):
                        self._process_parameters(
                            param,
                            data_classes,
                            enums,
                            generated_structs,
                            generated_enums,
                        )
                elif item["type"] == "event":
                    for param in item["inputs"]:
                        self._process_parameters(
                            param,
                            data_classes,
                            enums,
                            generated_structs,
                            generated_enums,
                        )

            return {
                "abiPath": self.abi_file_path,
                "contractName": self.contract_name,
                "methods": methods,
                "dataClasses": data_classes,
                "enums": enums,
            }
        except Exception as e:
            raise ABIHandlerError(f"Error preparing template data: {str(e)}") from e

    def _process_parameters(
        self, param, data_classes, enums, generated_structs, generated_enums
    ):
        if param["type"] == "tuple" and param["internalType"] not in generated_structs:
            struct_name = SolidityConverter._get_struct_name(param["internalType"])
            properties = [
                {
                    "name": comp["name"],
                    "type": SolidityConverter.convert_type(
                        comp["type"], comp.get("internalType")
                    ),
                }
                for comp in param["components"]
            ]
            data_classes.append({"name": struct_name, "properties": properties})
            generated_structs.add(param["internalType"])
        elif (
            "enum " in param["internalType"]
            and param["internalType"] not in generated_enums
        ):
            enum_name = SolidityConverter._get_struct_name(param["internalType"])
            enum_values = [
                {"name": item["name"], "value": item["value"]}
                for item in param["components"]
            ]
            enums.append({"name": enum_name, "values": enum_values})
            generated_enums.add(param["internalType"])

    def _process_function(self, function_item: Dict[str, Any]) -> Dict[str, Any]:
        original_name = function_item["name"]
        method_name = to_python_conventional_name(original_name)

        input_types = self._generate_function_input_args_with_types(function_item)
        output_types = [
            SolidityConverter.convert_type(o["type"], o.get("internalType"))
            for o in function_item.get("outputs", [])
        ]
        output_str = (
            "None"
            if not output_types
            else (
                output_types[0]
                if len(output_types) == 1
                else f'Tuple[{", ".join(output_types)}]'
            )
        )

        return {
            "name": method_name,
            "inputs": input_types,
            "outputType": output_str,
            "originalName": original_name,
        }

    def _generate_function_input_args_with_types(
        self, function_item: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        input_args = []
        unnamed_arg_counters = {}  # Track unnamed arguments of each type

        for input_item in function_item.get("inputs", []):
            input_type = SolidityConverter.convert_type(
                input_item["type"], input_item.get("internalType")
            )

            # Regex to transform type names like 'list[int]' into 'int_list'
            base_name = re.sub(r"list\[(\w+)\]", r"\1_list", input_type.lower())

            input_name = input_item.get("name")
            if not input_name:
                # If the argument is unnamed, use the base_name with a counter to create a unique name
                unnamed_arg_counters[base_name] = (
                    unnamed_arg_counters.get(base_name, -1) + 1
                )
                input_name = f"{base_name}_arg{unnamed_arg_counters[base_name]}"

            python_input_name = to_python_conventional_name(input_name)

            if input_item["type"] == "tuple":
                struct_name = SolidityConverter._get_struct_name(
                    input_item["internalType"]
                )
                properties = [
                    {
                        "name": component["name"],
                        "type": SolidityConverter.convert_type(
                            component["type"], component.get("internalType")
                        ),
                    }
                    for component in input_item["components"]
                ]
                destructured_args = ", ".join(
                    [f"{python_input_name}.{prop['name']}" for prop in properties]
                )
                input_args.append(
                    {
                        "name": python_input_name,
                        "type": struct_name,
                        "isTuple": True,
                        "destructuredArgs": f"({destructured_args})",
                    }
                )
            else:
                input_args.append(
                    {"name": python_input_name, "type": input_type, "isTuple": False}
                )

        return input_args

    def _render_template(self, data: Dict[str, Any]) -> str:
        partials = {
            get_filename_without_extension(partial_path): compile_partial(partial_path)
            for partial_path in _get_partials_files()
        }

        with open(_get_template_file(), "r") as file:
            template = file.read()

        compiler = Compiler()
        template = compiler.compile(template)
        return template(data, partials=partials)
