from cow_py.common.cow_error import (
    CowError,
)  # Adjust the import path according to your project structure


def test_cow_error_inheritance():
    # Test that CowError is a subclass of Exception
    assert issubclass(CowError, Exception)


def test_cow_error_initialization():
    # Test CowError initialization with a message and error_code
    message = "An error occurred"
    error_code = 1001
    error = CowError(message, error_code)

    assert str(error) == message
    assert error.error_code == error_code


def test_cow_error_initialization_without_error_code():
    # Test CowError initialization with only a message
    message = "An error occurred"
    error = CowError(message)

    assert str(error) == message
    assert error.error_code is None
