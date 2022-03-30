from pcapi.model_creators.generic_creators import create_offerer
from pcapi.models.api_errors import ApiErrors
from pcapi.validation.models.offerer import validate


def test_should_return_error_message_when_siren_has_not_exactly_9_characters():
    # Given
    offerer = create_offerer(siren="1234")
    api_errors = ApiErrors()

    # When
    api_error = validate(offerer, api_errors)

    # Then
    assert api_error.errors["siren"] == ["Ce code SIREN est invalide"]


def test_should_not_return_error_message_when_siren_has_exactly_9_characters():
    # Given
    offerer = create_offerer(siren="123456789")
    api_errors = ApiErrors()

    # When
    api_error = validate(offerer, api_errors)

    # Then
    assert not api_error.errors


def test_should_return_error_message_when_siren_has_no_characters():
    # Given
    offerer = create_offerer(siren="")
    api_errors = ApiErrors()

    # When
    api_error = validate(offerer, api_errors)

    # Then
    assert api_error.errors["siren"] == ["Ce code SIREN est invalide"]
