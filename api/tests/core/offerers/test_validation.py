import pytest

from pcapi.core.offerers.validation import validate_coordinates
from pcapi.models.api_errors import ApiErrors


def test_validate_coordinates_raises_an_api_errors_if_latitude_is_not_a_decimal():
    # when
    with pytest.raises(ApiErrors) as e:
        validate_coordinates("48°4565", None)

    # then
    assert e.value.errors["latitude"] == ["Format incorrect"]


def test_validate_coordinates_raises_an_api_errors_if_longitude_is_not_a_decimal():
    # when
    with pytest.raises(ApiErrors) as e:
        validate_coordinates(None, "48°4565")

    # then
    assert e.value.errors["longitude"] == ["Format incorrect"]


def test_validate_coordinates_raises_an_api_errors_for_both_latitude_and_longitude():
    # when
    with pytest.raises(ApiErrors) as e:
        validate_coordinates("53°4565", "48°4565")

    # then
    assert e.value.errors["latitude"] == ["Format incorrect"]
    assert e.value.errors["longitude"] == ["Format incorrect"]


def test_validate_coordinates_raises_an_api_errors_if_latitude_is_greater_than_90():
    # when
    with pytest.raises(ApiErrors) as e:
        validate_coordinates(92.543, None)

    # then
    assert e.value.errors["latitude"] == ["La latitude doit être comprise entre -90.0 et +90.0"]


def test_validate_coordinates_raises_an_api_errors_if_latitude_is_lower_than_minus_90():
    # when
    with pytest.raises(ApiErrors) as e:
        validate_coordinates(-92.543, None)

    # then
    assert e.value.errors["latitude"] == ["La latitude doit être comprise entre -90.0 et +90.0"]


def test_validate_coordinates_raises_an_api_errors_if_longitude_is_greater_than_180():
    # when
    with pytest.raises(ApiErrors) as e:
        validate_coordinates(None, 182.66464)

    # then
    assert e.value.errors["longitude"] == ["La longitude doit être comprise entre -180.0 et +180.0"]


def test_validate_coordinates_raises_an_api_errors_if_longitude_is_lower_than_minus_180():
    # when
    with pytest.raises(ApiErrors) as e:
        validate_coordinates(None, -182.66464)

    # then
    assert e.value.errors["longitude"] == ["La longitude doit être comprise entre -180.0 et +180.0"]


def test_validate_coordinates_raises_an_api_errors_if_both_latitude_and_longitude_are_out_of_bounds():
    # when
    with pytest.raises(ApiErrors) as e:
        validate_coordinates(93.46, -182.66464)

    # then
    assert e.value.errors["latitude"] == ["La latitude doit être comprise entre -90.0 et +90.0"]
    assert e.value.errors["longitude"] == ["La longitude doit être comprise entre -180.0 et +180.0"]
