from cow_py.common.cow_error import CowError


def test_cow_error_inheritance():
    assert issubclass(CowError, Exception)


def test_cow_error_initialization():
    message = "An error occurred"
    error_code = 1001
    error = CowError(message, error_code)

    assert str(error) == message
    assert error.error_code == error_code


def test_cow_error_initialization_without_error_code():
    message = "An error occurred"
    error = CowError(message)

    assert str(error) == message
    assert error.error_code is None
