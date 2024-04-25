import pytest

from cow_py.codegen.solidity_converter import SolidityConverter, SolidityConverterError


def test_solidity_converter_get_struct_name():
    internal_type = "struct MyStruct"
    expected_result = "MyStruct"
    result = SolidityConverter._get_struct_name(internal_type)
    assert result == expected_result


def test_solidity_converter_get_struct_name_invalid_internal_type():
    internal_type = "uint256"
    with pytest.raises(SolidityConverterError):
        SolidityConverter._get_struct_name(internal_type)


def test_solidity_converter_convert_type_enum():
    solidity_type = "enum MyEnum"
    internal_type = ""
    expected_result = "MyEnum"
    result = SolidityConverter.convert_type(solidity_type, internal_type)
    assert result == expected_result


def test_solidity_converter_convert_type_array():
    solidity_type = "uint256[]"
    internal_type = ""
    expected_result = "List[int]"
    result = SolidityConverter.convert_type(solidity_type, internal_type)
    assert result == expected_result


def test_solidity_converter_convert_type_tuple():
    solidity_type = "tuple"
    internal_type = "struct MyStruct"
    expected_result = "MyStruct"
    result = SolidityConverter.convert_type(solidity_type, internal_type)
    assert result == expected_result


def test_solidity_converter_convert_type_fixed_size_array():
    solidity_type = "uint256[3]"
    internal_type = ""
    expected_result = "Tuple[int, int, int]"
    result = SolidityConverter.convert_type(solidity_type, internal_type)
    assert result == expected_result


def test_solidity_converter_convert_type_unknown_type():
    solidity_type = "unknown_type"
    internal_type = ""
    expected_result = "Any"
    result = SolidityConverter.convert_type(solidity_type, internal_type)
    assert result == expected_result


def test_solidity_converter_extract_enum_name():
    internal_type = "enum MyEnum.Option"
    expected_result = "MyEnum_Option"
    result = SolidityConverter._extract_enum_name(internal_type)
    assert result == expected_result


def test_solidity_converter_convert_array_or_basic_type_dynamic_array():
    solidity_type = "address[]"
    expected_result = "List[str]"
    result = SolidityConverter._convert_array_or_basic_type(solidity_type)
    assert result == expected_result


def test_solidity_converter_convert_array_or_basic_type_fixed_size_array():
    solidity_type = "bool[5]"
    expected_result = "Tuple[bool, bool, bool, bool, bool]"
    result = SolidityConverter._convert_array_or_basic_type(solidity_type)
    assert result == expected_result


def test_solidity_converter_convert_array_or_basic_type_basic_type():
    solidity_type = "bytes32"
    expected_result = "HexBytes"
    result = SolidityConverter._convert_array_or_basic_type(solidity_type)
    assert result == expected_result
