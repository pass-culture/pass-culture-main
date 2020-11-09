from unittest.mock import patch

from tests.conftest import TestClient


class Post:
    class Returns200:
        @patch('pcapi.routes.beneficiaries.beneficiary_job.delay')
        def when_has_exact_payload(self, mocked_beneficiary_job, app):
            # Given
            data = {'id': '5'}

            # When
            response = TestClient(app.test_client()) \
                .post('/beneficiaries/application_update', json=data)

            # Then
            assert response.status_code == 200
            mocked_beneficiary_job.assert_called_once_with(5)

    class Returns400:
        @patch('pcapi.routes.beneficiaries.beneficiary_job.delay')
        def when_no_payload(self, mocked_beneficiary_job, app):
            # When
            response = TestClient(app.test_client()) \
                .post('/beneficiaries/application_update')

            # Then
            assert response.status_code == 400
            mocked_beneficiary_job.assert_not_called()

        @patch('pcapi.routes.beneficiaries.beneficiary_job.delay')
        def when_has_wrong_payload(self, mocked_beneficiary_job, app):
            # Given
            data = {'next-id': '5'}

            # When
            response = TestClient(app.test_client()) \
                .post('/beneficiaries/application_update', json=data)

            # Then
            assert response.status_code == 400
            mocked_beneficiary_job.assert_not_called()

        @patch('pcapi.routes.beneficiaries.beneficiary_job.delay')
        def when_id_is_not_a_number(self, mocked_beneficiary_job, app):
            # Given
            data = {'id': 'cinq'}

            # When
            response = TestClient(app.test_client()) \
                .post('/beneficiaries/application_update', json=data)

            # Then
            assert response.status_code == 400
            mocked_beneficiary_job.assert_not_called()
