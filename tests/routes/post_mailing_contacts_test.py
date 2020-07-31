import pytest
from unittest.mock import patch, MagicMock
from tests.conftest import TestClient
from models import ApiErrors
from workers.mailing_contacts_job import mailing_contacts_job

class Post:
    class Returns201:
        @patch('routes.mailing_contacts.validate_save_mailing_contact_request')
        @patch('routes.mailing_contacts.mailing_contacts_job.delay')
        def when_contact_has_successfully_been_saved(self, mocked_add_contact_job, validate_request, app):
            # Given
            data = {
                "email": "jeune@example.com",
                "dateOfBirth": "02/02/2003",
                "departmentCode": "98"
            }

            # When
            response = TestClient(app.test_client()).post('/mailing-contacts', json=data)

            # Then
            mocked_add_contact_job.assert_called_once_with(data["email"], data["dateOfBirth"], data["departmentCode"])
            validate_request.assert_called_once_with(data)
            assert response.status_code == 201

    class Returns400:
        @patch('routes.mailing_contacts.validate_save_mailing_contact_request')
        def when_payload_validation_fails(self, validate_request, app):
            # Given
            data = {
                "dateOfBirth": "02/02/2003",
                "department_code": "98"
            }

            validate_request.side_effect = ApiErrors({'email': 'L\'email est manquant'})

            # When
            response = TestClient(app.test_client()).post('/mailing-contacts', json=data)

            # Then
            validate_request.assert_called_once_with(data)
            assert response.status_code == 400