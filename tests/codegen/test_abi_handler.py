import pytest

from cow_py.codegen.abi_handler import (
    to_python_conventional_name,
    get_filename_without_extension,
    _get_template_file,
    _get_partials_files,
    compile_partial,
    ABIHandler,
    FileAbiLoader,
)

from unittest.mock import mock_open


@pytest.mark.parametrize(
    "input_name, expected_output",
    [
        # ("GPv2Order_Data", "gp_v2_order_data"),
        ("simpleTest", "simple_test"),
        ("ThisIsATest", "this_is_a_test"),
        ("number2IsHere", "number_2_is_here"),
        ("AnotherTest123", "another_test_123"),
        ("JSONData", "json_data"),
        # ("GPv2Order_Data_arg_1", "gp_v2_order_data_arg_1"),
    ],
)
def test_to_python_conventional_name(input_name, expected_output):
    assert to_python_conventional_name(input_name) == expected_output


def test_compile_partial(mocker):
    # Test that compile_partial correctly compiles a partial template
    mocked_file_content = "test content"
    mocked_compiled_content = "compiled content"

    mocker.patch("builtins.open", mock_open(read_data=mocked_file_content))
    mocker.patch("pybars.Compiler.compile", return_value=mocked_compiled_content)
    result = compile_partial("fake_path")
    assert result == mocked_compiled_content


def test_get_filename_without_extension():
    # Test that get_filename_without_extension correctly removes the extension
    assert get_filename_without_extension("folder/test.py") == "test"


def test_get_template_file():
    # Test that _get_template_file returns the correct template file path
    assert _get_template_file().endswith("contract_template.hbs")


def test_get_partials_files():
    # Test that _get_partials_files returns the correct list of partial files
    assert all([f.endswith(".hbs") for f in _get_partials_files()])


@pytest.fixture
def abi_handler():
    return ABIHandler("TestContract", "/fake/path/to/abi.json")


def test_abi_handler_generate(mocker, abi_handler):
    # Test that ABIHandler.generate correctly generates Python code from an ABI
    mocked_abi_data = [
        {"type": "function", "name": "doSomething", "inputs": [], "outputs": []}
    ]
    mocker.patch(
        "cow_py.codegen.abi_handler.FileAbiLoader.load_abi",
        return_value=mocked_abi_data,
    )
    mocker.patch(
        "cow_py.codegen.abi_handler.ABIHandler._prepare_template_data",
        return_value={"methods": []},
    )
    mocker.patch(
        "cow_py.codegen.abi_handler.ABIHandler._render_template",
        return_value="class MyContract:\n    pass",
    )

    # Run the method
    result = abi_handler.generate()

    # Verify the output
    assert (
        result == "class MyContract:\n    pass"
    ), "Generated Python code does not match expected output."


def test_abi_handler_prepare_template_data(mocker, abi_handler):
    # Test that ABIHandler._prepare_template_data correctly processes the ABI
    sample_abi = [
        {
            "type": "function",
            "name": "setValue",
            "inputs": [{"name": "value", "type": "uint256"}],
            "outputs": [],
        },
        {
            "type": "event",
            "name": "ValueChanged",
            "inputs": [{"name": "value", "type": "uint256"}],
        },
    ]

    mocker.patch.object(FileAbiLoader, "load_abi", return_value=sample_abi)

    mocker.patch.object(
        abi_handler,
        "_process_function",
        return_value={
            "name": "set_value",
            "inputs": ["uint256"],
            "outputType": "None",
            "originalName": "setValue",
        },
    )
    mocker.patch.object(abi_handler, "_process_parameters", autospec=True)

    result = abi_handler._prepare_template_data()

    assert result["abiPath"] == "/fake/path/to/abi.json"
    assert result["contractName"] == "TestContract"
    assert len(result["methods"]) == 1
    assert result["methods"][0]["name"] == "set_value"
    assert "dataClasses" in result
    assert "enums" in result


def test_abi_handler_process_parameters(abi_handler):
    # Test that ABIHandler._process_parameters correctly processes function parameters
    param = {
        "type": "tuple",
        "internalType": "struct Value",
        "components": [
            {"name": "x", "type": "uint256", "internalType": "uint256"},
            {"name": "y", "type": "uint256", "internalType": "uint256"},
        ],
    }
    data_classes = []
    enums = []
    generated_structs = set()
    generated_enums = set()

    expected_data_class = {
        "name": "Value",
        "properties": [
            {"name": "x", "type": "int"},
            {"name": "y", "type": "int"},
        ],
    }

    abi_handler._process_parameters(
        param, data_classes, enums, generated_structs, generated_enums
    )

    assert "struct Value" in generated_structs
    assert data_classes[0] == expected_data_class


def test_abi_handler_process_function(abi_handler, mocker):
    # Test that ABIHandler._process_function correctly processes a function item
    function_item = {
        "type": "function",
        "name": "getValue",
        "inputs": [{"name": "key", "type": "uint256", "internalType": "uint256"}],
        "outputs": [{"name": "result", "type": "uint256", "internalType": "uint256"}],
    }

    result = abi_handler._process_function(function_item)

    expected_result = {
        "name": "get_value",
        "inputs": [{"name": "key", "type": "int", "isTuple": False}],
        "outputType": "int",
        "originalName": "getValue",
    }

    assert result == expected_result


def test_abi_handler_render_template(abi_handler, mocker):
    # Test that ABIHandler._render_template correctly renders the template with data
    template_data = {
        "abiPath": "/fake/path/to/abi.json",
        "contractName": "TestContract",
        "methods": [
            {
                "name": "set_value",
                "inputs": ["uint256"],
                "outputType": "uint256",
                "originalName": "setValue",
            }
        ],
        "dataClasses": [],
        "enums": [],
    }
    template_string = "class {{ contractName }}:\n    pass"
    expected_rendered_output = "class TestContract:\n    pass"

    mocker.patch("builtins.open", mocker.mock_open(read_data=template_string))

    mocker.patch(
        "pybars.Compiler.compile",
        return_value=lambda x, **kwargs: expected_rendered_output,
    )

    result = abi_handler._render_template(template_data)

    assert result == expected_rendered_output
