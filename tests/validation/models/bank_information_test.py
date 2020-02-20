from models import ApiErrors
from tests.model_creators.generic_creators import create_bank_information
from validation.models.bank_information import validate


def test_should_return_error_message_when_iban_is_invalid():
    # Given
    bank_information = create_bank_information(iban="FR76")
    api_errors = ApiErrors()

    # When
    api_error = validate(bank_information, api_errors)

    # Then
    assert api_error.errors['iban'] == ['L’IBAN renseigné ("FR76") est invalide']


def test_should_return_error_message_when_bic_is_invalid():
    # Given
    bank_information = create_bank_information(bic="1234")
    api_errors = ApiErrors()

    # When
    api_error = validate(bank_information, api_errors)

    # Then
    assert api_error.errors['bic'] == ['Le BIC renseigné ("1234") est invalide']


def test_should_return_error_messages_when_iban_and_bic_are_invalid():
    # Given
    bank_information = create_bank_information(bic="1234", iban="1234")
    api_errors = ApiErrors()

    # When
    api_error = validate(bank_information, api_errors)

    # Then
    assert api_error.errors == {
        'bic': ['Le BIC renseigné ("1234") est invalide'],
        'iban': ['L’IBAN renseigné ("1234") est invalide']
    }


def test_should_return_no_error_message_when_iban_and_bic_are_valid():
    # Given
    bank_information = create_bank_information()
    api_errors = ApiErrors()

    # When
    api_error = validate(bank_information, api_errors)

    # Then
    assert api_error.errors == {}
