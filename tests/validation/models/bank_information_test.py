from pcapi.models import ApiErrors
from pcapi.models.bank_information import BankInformationStatus
from pcapi.model_creators.generic_creators import create_bank_information
from pcapi.validation.models.bank_information import validate


def test_should_return_error_message_when_iban_is_invalid():
    # Given
    bank_information = create_bank_information(iban="FR76")
    api_errors = ApiErrors()

    # When
    api_error = validate(bank_information, api_errors)

    # Then
    assert api_error.errors['iban'] == [
        'L’IBAN renseigné ("FR76") est invalide']


def test_should_return_error_message_when_bic_is_invalid():
    # Given
    bank_information = create_bank_information(bic="1234")
    api_errors = ApiErrors()

    # When
    api_error = validate(bank_information, api_errors)

    # Then
    assert api_error.errors['bic'] == [
        'Le BIC renseigné ("1234") est invalide']


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


def test_should_return_no_error_message_when_iban_and_bic_are_valid_and_status_accepted():
    # Given
    bank_information = create_bank_information()
    api_errors = ApiErrors()

    # When
    api_error = validate(bank_information, api_errors)

    # Then
    assert api_error.errors == {}


def test_should_return_an_error_if_status_is_not_accepted_and_bic_or_iban_is_present():
    # Given
    bank_information = create_bank_information(
        status=BankInformationStatus.DRAFT)
    api_errors = ApiErrors()

    # When
    api_error = validate(bank_information, api_errors)

    # Then
    assert api_error.errors == {
        'bic': ['Le BIC doit être vide pour le statut DRAFT'],
        'iban': ['L’IBAN doit être vide pour le statut DRAFT']
    }


def test_should_not_return_an_error_if_status_is_not_accepted_and_bic_and_iban_are_empty():
    # Given
    bank_information = create_bank_information(bic=None,
                                               iban=None,
                                               status=BankInformationStatus.DRAFT)
    api_errors = ApiErrors()

    # When
    api_error = validate(bank_information, api_errors)

    # Then
    assert api_error.errors == {}
