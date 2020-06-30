from tests.conftest import TestClient

class Post:
    class Returns200:
        def when_has_exact_payload(self, app):
            # Given
            data = {'id': '5'}

            # When
            response = TestClient(app.test_client()) \
                .post('/beneficiaries/application_update', json=data)

            # Then
            assert response.status_code == 200

    class Returns400:
        def when_no_payload(self, app):
            # When
            response = TestClient(app.test_client()) \
                .post('/beneficiaries/application_update')

            # Then
            assert response.status_code == 400

        def when_has_wrong_payload(self, app):
            # Given
            data = {'next-id': '5'}

            # When
            response = TestClient(app.test_client()) \
                .post('/beneficiaries/application_update', json=data)

            # Then
            assert response.status_code == 400

        def when_id_is_not_a_number(self, app):
            # Given
            data = {'id': 'cinq'}

            # When
            response = TestClient(app.test_client()) \
                .post('/beneficiaries/application_update', json=data)

            # Then
            assert response.status_code == 400

