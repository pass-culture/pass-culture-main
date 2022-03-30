from datetime import datetime

from pcapi.model_creators.generic_creators import create_stock
from pcapi.models.api_errors import ApiErrors
from pcapi.validation.models.stock import validate


def test_should_return_error_message_when_stock_is_negative():
    # Given
    stock = create_stock(quantity=-1)
    api_errors = ApiErrors()

    # When
    api_error = validate(stock, api_errors)

    # Then
    assert api_error.errors["quantity"] == ["La quantité doit être positive."]


def test_should_not_return_error_message_when_stock_is_positive():
    # Given
    stock = create_stock(quantity=1)
    api_errors = ApiErrors()

    # When
    api_error = validate(stock, api_errors)

    # Then
    assert not api_error.errors


def test_should_not_return_error_message_when_stock_is_unlimited():
    # Given
    stock = create_stock(quantity=None)
    api_errors = ApiErrors()

    # When
    api_error = validate(stock, api_errors)

    # Then
    assert not api_error.errors


def test_should_not_return_error_message_when_datetime_is_valid():
    # Given
    stock = create_stock(beginning_datetime=datetime(2020, 1, 1))
    api_errors = ApiErrors()

    # When
    api_error = validate(stock, api_errors)

    # Then
    assert not api_error.errors
