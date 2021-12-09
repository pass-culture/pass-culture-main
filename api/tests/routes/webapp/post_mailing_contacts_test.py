from unittest.mock import MagicMock

from pcapi.workers.mailing_contacts_job import mailing_contacts_job

from tests.conftest import TestClient


class Returns201Test:
    def when_contact_has_successfully_been_saved(self, app):
        # Given
        mailing_contacts_job.delay = MagicMock()
        data = {"email": "jeune@example.com", "dateOfBirth": "2003-02-02", "departmentCode": "98"}

        # When
        response = TestClient(app.test_client()).post("/mailing-contacts", json=data)

        # Then
        mailing_contacts_job.delay.assert_called_once_with(data["email"], data["dateOfBirth"], data["departmentCode"])
        assert response.status_code == 201


class Returns400Test:
    def when_payload_validation_fails(self, app):
        # Given
        data = {"dateOfBirth": "2003-02-02", "department_code": "98"}

        # When
        response = TestClient(app.test_client()).post("/mailing-contacts", json=data)

        # Then
        assert response.json == {"email": ["Ce champ est obligatoire"], "departmentCode": ["Ce champ est obligatoire"]}
        assert response.status_code == 400
