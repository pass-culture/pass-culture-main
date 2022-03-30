from pcapi.model_creators.generic_creators import create_offerer
from pcapi.models.api_errors import ApiErrors
from pcapi.validation.models.has_address_mixin import validate


def test_should_return_error_message_when_postal_code_is_invalid():
    # Given
    offerer = create_offerer(postal_code="fgvbhjnk")
    api_errors = ApiErrors()

    # When
    api_error = validate(offerer, api_errors)

    # Then
    assert api_error.errors["postalCode"] == ["Ce code postal est invalide"]


def test_should_not_return_error_message_when_postal_code_is_valid():
    # Given
    offerer = create_offerer(postal_code="75000")
    api_errors = ApiErrors()

    # When
    api_error = validate(offerer, api_errors)

    # Then
    assert not api_error.errors
