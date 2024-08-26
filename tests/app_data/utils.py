from cow_py.app_data.utils import stringify_deterministic


def test_stringify_deterministic_simple_object():
    node = {"c": 6, "b": [4, 5], "a": 3, "z": None}
    actual = stringify_deterministic(node)
    expected = '{"a":3,"b":[4,5],"c":6,"z":null}'
    assert actual == expected


def test_stringify_deterministic_object_with_empty_string():
    node = {"a": 3, "z": ""}
    actual = stringify_deterministic(node)
    expected = '{"a":3,"z":""}'
    assert actual == expected


def test_stringify_deterministic_nested_object():
    node = {"a": {"b": {"c": [1, 2, 3, None]}}}
    actual = stringify_deterministic(node)
    expected = '{"a":{"b":{"c":[1,2,3,null]}}}'
    assert actual == expected


def test_stringify_deterministic_array_with_objects():
    node = [{"z": 1, "a": 2}]
    actual = stringify_deterministic(node)
    expected = '[{"a":2,"z":1}]'
    assert actual == expected


def test_stringify_deterministic_nested_array_objects():
    node = [{"z": [[{"y": 1, "b": 2}]], "a": 2}]
    actual = stringify_deterministic(node)
    expected = '[{"a":2,"z":[[{"b":2,"y":1}]]}]'
    assert actual == expected


def test_stringify_deterministic_array_with_none():
    node = [1, None]
    actual = stringify_deterministic(node)
    expected = "[1,null]"
    assert actual == expected


def test_stringify_deterministic_array_with_empty_string():
    node = [1, ""]
    actual = stringify_deterministic(node)
    expected = '[1,""]'
    assert actual == expected
