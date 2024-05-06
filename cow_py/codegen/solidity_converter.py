import re
from typing import Optional

SOLIDITY_TO_PYTHON_TYPES = {
    "address": "str",
    "bool": "bool",
    "string": "str",
    "bytes": "HexBytes",
    "uint": "int",
    "int": "int",
}
DYNAMIC_SOLIDITY_TYPES = {
    f"{prefix}{i*8 if prefix != 'bytes' else i}": (
        "int" if prefix != "bytes" else "HexBytes"
    )
    for prefix in ["uint", "int", "bytes"]
    for i in range(1, 33)
}
SOLIDITY_TO_PYTHON_TYPES.update(DYNAMIC_SOLIDITY_TYPES)


class SolidityConverterError(Exception):
    """Raised when an error occurs in the SolidityConverter."""

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

        Raises:
            SolidityConverterError: If the internal type is not in the expected format.
        """
        if not internal_type or "struct " not in internal_type:
            raise SolidityConverterError(
                f"Invalid internal type for struct: {internal_type}"
            )
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
        if re.search(r"enum", internal_type) or (re.search(r"enum", solidity_type)):
            return cls._extract_enum_name(internal_type, solidity_type)
        elif solidity_type == "tuple":
            return cls._get_struct_name(internal_type)
        else:
            return cls._convert_array_or_basic_type(solidity_type)

    @staticmethod
    def _extract_enum_name(
        internal_type: Optional[str], solidity_type: Optional[str] = None
    ) -> str:
        if internal_type and re.search(r"enum", internal_type):
            return internal_type.replace("enum ", "").replace(".", "_")
        elif solidity_type and re.search(r"enum", solidity_type):
            return solidity_type.replace("enum ", "").replace(".", "_")
        raise SolidityConverterError(f"Invalid internal type for enum: {internal_type}")

    @staticmethod
    def _convert_array_or_basic_type(solidity_type: str) -> str:
        array_match = re.match(r"(.+?)(\[\d*\])", solidity_type)
        if array_match:
            base_type, array_size = array_match.groups()
            if array_size == "[]":
                return f'List[{SOLIDITY_TO_PYTHON_TYPES.get(base_type, "Any")}]'
            else:
                size = int(array_size[1:-1])
                return f'Tuple[{", ".join([SOLIDITY_TO_PYTHON_TYPES.get(base_type, "Any")] * size)}]'
        else:
            return SOLIDITY_TO_PYTHON_TYPES.get(solidity_type, "Any")
