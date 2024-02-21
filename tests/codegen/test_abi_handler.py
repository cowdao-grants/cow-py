import pytest
from cow_py.codegen.abi_handler import to_python_conventional_name


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
