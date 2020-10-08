import pytest

from pcapi.models import ApiErrors
from pcapi.validation.routes.mailing_contacts import validate_save_mailing_contact_request

class ValidateSaveMailingContactRequestTest:
    def should_raise_exception_when_email_not_provided(self):
        # Given
        request = {
            "dateOfBirth": "2003-03-05",
            "departmentCode": "27"
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
            "departmentCode": "27"
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
            "dateOfBirth": "2003-03-05"
        }

        # When
        with pytest.raises(ApiErrors) as error:
            validate_save_mailing_contact_request(request)

        # Then
        assert error.value.errors['department_code'] == ['Le code département est manquant']
