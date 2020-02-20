from datetime import datetime

from models import ApiErrors
from tests.model_creators.generic_creators import create_stock
from validation.models.stock import validate


def test_should_return_error_message_when_stock_is_negative():
    # Given
    stock = create_stock(available=-1)
    api_errors = ApiErrors()

    # When
    api_error = validate(stock, api_errors)

    # Then
    assert api_error.errors['available'] == ['Le stock doit être positif']


def test_should_return_error_message_when_beginning_datetime_is_posterior_to_end_datetime():
    # Given
    stock = create_stock(beginning_datetime=datetime(2020, 1, 5), end_datetime=datetime(2020, 1, 2))
    api_errors = ApiErrors()

    # When
    api_error = validate(stock, api_errors)

    # Then
    assert api_error.errors['endDatetime'] == ['La date de fin de l’événement doit être postérieure à la date de début']


def test_should_not_return_error_message_when_stock_is_positive():
    # Given
    stock = create_stock(available=1)
    api_errors = ApiErrors()

    # When
    api_error = validate(stock, api_errors)

    # Then
    assert api_error.errors == {}


def test_should_not_return_error_message_when_stock_is_unlimited():
    # Given
    stock = create_stock(available=None)
    api_errors = ApiErrors()

    # When
    api_error = validate(stock, api_errors)

    # Then
    assert api_error.errors == {}


def test_should_not_return_error_message_when_datetimes_are_valid():
    # Given
    stock = create_stock(beginning_datetime=datetime(2020, 1, 1), end_datetime=datetime(2020, 1, 2))
    api_errors = ApiErrors()

    # When
    api_error = validate(stock, api_errors)

    # Then
    assert api_error.errors == {}
