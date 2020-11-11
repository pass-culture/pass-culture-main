import pytest

from pcapi.models import ApiErrors
from pcapi.validation.routes.bookings import check_page_format_is_number


def test_should_raise_error_when_page_number_is_not_a_number():
    # Given
    page = "foobar"

    # When
    with pytest.raises(ApiErrors) as error:
        check_page_format_is_number(page)

    # Then
    assert error.value.errors == {"global": ["L'argument 'page' foobar n'est pas valide"]}


def test_should_not_raise_error_when_page_number_is_a_string_containing_number():
    # Given
    page = "1"

    # When
    try:
        check_page_format_is_number(page)
    except:
        assert False

    # Then
    assert True


def test_should_raise_error_when_page_number_is_inferior_to_1():
    # Given
    page = 0

    # When
    with pytest.raises(ApiErrors) as error:
        check_page_format_is_number(page)

    # Then
    assert error.value.errors == {"global": ["L'argument 'page' 0 n'est pas valide"]}
