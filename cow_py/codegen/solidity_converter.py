# Constants
SOLIDITY_TO_PYTHON_TYPES = {
    "address": "str",
    "bool": "bool",
    "string": "str",
    "bytes": "HexBytes",
    "uint": "int",
    "int": "int",
}
DYNAMIC_SOLIDITY_TYPES = {
    f"{prefix}{i*8 if prefix != 'bytes' else i}": "int"
    if prefix != "bytes"
    else "HexBytes"
    for prefix in ["uint", "int", "bytes"]
    for i in range(1, 33)
}
SOLIDITY_TO_PYTHON_TYPES.update(DYNAMIC_SOLIDITY_TYPES)


class InvalidABIError(Exception):
    """Raised when an invalid ABI is provided."""

    pass


class SolidityConverter:
    """
    Converts Solidity data types to equivalent Python data types.

    This class provides methods to map Solidity types as found in Ethereum smart contracts' ABIs
    to Python types, facilitating the generation of Python classes and methods to interact with these contracts.

    Methods:
        convert_type: Converts a Solidity data type to its Python equivalent.
    """

    @staticmethod
    def _get_struct_name(internal_type: str) -> str:
        """
        Extracts the struct name from a given internal type.

        Args:
            internal_type (str): The internal type string from an ABI, often representing a struct.

        Returns:
            str: The extracted name of the struct.
        """
        return internal_type.replace("struct ", "").replace(".", "_").replace("[]", "")

    @classmethod
    def convert_type(cls, solidity_type: str, internal_type: str) -> str:
        """
        Converts a Solidity type to the corresponding Python type.

        Args:
            solidity_type (str): The Solidity type as specified in the contract's ABI.
            internal_type (str): The internal type representation, used for more complex data structures.

        Returns:
            str: The Python type equivalent to the given Solidity type.
        """
        if internal_type and "enum" in internal_type:
            return internal_type.split("enum")[-1].split(".")[-1].strip()
        if "[]" in solidity_type:
            base_type = solidity_type.replace("[]", "")
            return f'List[{SOLIDITY_TO_PYTHON_TYPES.get(base_type, "Any")}]'
        elif "[" in solidity_type and "]" in solidity_type:
            base_type = solidity_type.split("[")[0]
            return f'List[{SOLIDITY_TO_PYTHON_TYPES.get(base_type, "Any")}]'
        elif solidity_type == "tuple":
            return cls._get_struct_name(internal_type)
        return SOLIDITY_TO_PYTHON_TYPES.get(solidity_type, "Any")
