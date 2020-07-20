import pytest
from unittest.mock import patch, MagicMock
from tests.conftest import TestClient
from models import ApiErrors
from domain.beneficiary_contact.beneficiary_contact_exceptions import AddNewBeneficiaryContactException

class Post:
    class Returns200:
        @patch('routes.mailing_contacts.validate_save_mailing_contact_request')
        @patch('routes.mailing_contacts.add_contact_in_eligibility_list.execute')
        def when_contact_has_successfully_been_saved(self, add_contact, validate_request, app):
            # Given
            data = {
                "email": "toto@example.com",
                "date_of_birth": "02/02/2003",
                "department_code": "98"
            }

            # When
            response = TestClient(app.test_client()).post('/mailing_contacts', json=data)

            # Then
            add_contact.assert_called_once_with(data["email"], data["date_of_birth"], data["department_code"])
            validate_request.assert_called_once_with(data)
            assert response.status_code == 200

    class Returns400:
        @patch('routes.mailing_contacts.validate_save_mailing_contact_request')
        def when_payload_validation_fails(self, validate_request, app):
            # Given
            data = {
                "date_of_birth": "02/02/2003",
                "department_code": "98"
            }

            validate_request.side_effect = ApiErrors({'email': 'L\'email est manquant'})

            # When
            response = TestClient(app.test_client()).post('/mailing_contacts', json=data)

            # Then
            validate_request.assert_called_once_with(data)
            assert response.status_code == 400


        @patch('routes.mailing_contacts.validate_save_mailing_contact_request')
        @patch('routes.mailing_contacts.add_contact_in_eligibility_list.execute')
        def when_add_contact_fails(self, add_contact, validate_request, app):
            # Given
            data = {
                "email": "beneficiary@example.com",
                "date_of_birth": "02/02/2003",
                "department_code": "98"
            }

            validate_request = MagicMock()
            add_contact.side_effect = AddNewBeneficiaryContactException('mailjet', 'Impossible d\'ajouter le contact.')

            # When
            response = TestClient(app.test_client()).post('/mailing_contacts', json=data)

            # Then
            add_contact.assert_called_once_with(data["email"], data["date_of_birth"], data["department_code"])
            assert response.status_code == 400
