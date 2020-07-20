import pytest

from models import ApiErrors
from validation.routes.mailing_contacts import validate_save_mailing_contact_request

class ValidateSaveMailingContactRequestTest:
    def should_raise_exception_when_email_not_provided(self):
        # Given
        request = {
            "date_of_birth": "2003-03-05",
            "department_code": "27"
        }

        # When
        with pytest.raises(ApiErrors) as error:
            validate_save_mailing_contact_request(request)

        # Then
        assert error.value.errors['email'] == ['L\'email est manquant']

    def should_raise_exception_when_date_of_birth_not_provided(self):
        # Given
        request = {
            "email": "beneficiary@example.com",
            "department_code": "27"
        }

        # When
        with pytest.raises(ApiErrors) as error:
            validate_save_mailing_contact_request(request)

        # Then
        assert error.value.errors['date_of_birth'] == ['La date de naissance est manquante']

    def should_raise_exception_when_department_code_not_provided(self):
        # Given
        request = {
            "email": "beneficiary@example.com",
            "date_of_birth": "2003-03-05"
        }

        # When
        with pytest.raises(ApiErrors) as error:
            validate_save_mailing_contact_request(request)

        # Then
        assert error.value.errors['department_code'] == ['Le code département est manquant']
