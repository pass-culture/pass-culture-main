import pcapi.core.finance.factories as finance_factories
from pcapi.core.finance.models import BankInformationStatus
from pcapi.models.api_errors import ApiErrors
from pcapi.validation.models.bank_information import validate


class BankInformationValidationTest:
    def test_should_return_error_message_when_iban_is_invalid(self):
        # Given
        bank_information = finance_factories.BankInformationFactory.build(iban="FR76")
        api_errors = ApiErrors()

        # When
        api_error = validate(bank_information, api_errors)

        # Then
        assert api_error.errors["iban"] == ['L’IBAN renseigné ("FR76") est invalide']

    def test_should_return_error_message_when_bic_is_invalid(self):
        # Given
        bank_information = finance_factories.BankInformationFactory.build(bic="1234")
        api_errors = ApiErrors()

        # When
        api_error = validate(bank_information, api_errors)

        # Then
        assert api_error.errors["bic"] == ['Le BIC renseigné ("1234") est invalide']

    def test_should_return_error_messages_when_iban_and_bic_are_invalid(self):
        # Given
        bank_information = finance_factories.BankInformationFactory.build(bic="1234", iban="1234")
        api_errors = ApiErrors()

        # When
        api_error = validate(bank_information, api_errors)

        # Then
        assert api_error.errors == {
            "bic": ['Le BIC renseigné ("1234") est invalide'],
            "iban": ['L’IBAN renseigné ("1234") est invalide'],
        }

    def test_should_return_no_error_message_when_iban_and_bic_are_valid_and_status_accepted(self):
        # Given
        bank_information = finance_factories.BankInformationFactory.build()
        api_errors = ApiErrors()

        # When
        api_error = validate(bank_information, api_errors)

        # Then
        assert not api_error.errors

    def test_should_return_an_error_if_status_is_not_accepted_and_bic_or_iban_is_present(self):
        # Given
        bank_information = finance_factories.BankInformationFactory.build(status=BankInformationStatus.DRAFT)
        api_errors = ApiErrors()

        # When
        api_error = validate(bank_information, api_errors)

        # Then
        assert api_error.errors == {
            "bic": ["Le BIC doit être vide pour le statut DRAFT"],
            "iban": ["L’IBAN doit être vide pour le statut DRAFT"],
        }

    def test_should_not_return_an_error_if_status_is_not_accepted_and_bic_and_iban_are_empty(self):
        # Given
        bank_information = finance_factories.BankInformationFactory.build(
            bic=None, iban=None, status=BankInformationStatus.DRAFT
        )
        api_errors = ApiErrors()

        # When
        api_error = validate(bank_information, api_errors)

        # Then
        assert not api_error.errors
