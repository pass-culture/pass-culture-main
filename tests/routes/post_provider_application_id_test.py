from tests.conftest import clean_database, TestClient
from unittest.mock import call, patch
from workers.bank_information_job import synchronize_bank_informations

class Post:
    class Returns202:
        @patch('routes.providers.worker.redis_queue.enqueue_call')
        @clean_database
        def when_has_valid_provider_name_and_dossier_id(self, mock_add_to_redis_queue, app):
            # Given
            data = {'dossier_id': '666'}

            # When
            response = TestClient(app.test_client()).post('/providers/offerer/application_update', form=data)

            # Then
            assert response.status_code == 202
            assert mock_add_to_redis_queue.call_args_list == [
              call(func=synchronize_bank_informations, args=('666', 'offerer'))
            ]

    class Returns400:
        @patch('routes.providers.worker.redis_queue.enqueue_call')
        @clean_database
        def when_has_not_dossier_in_request_form_data(self, mock_add_to_redis_queue, app):
            # Given
            data = {'fake_key': '666'}

            # When
            response = TestClient(app.test_client()).post('/providers/offerer/application_update', form=data)

            # Then
            assert response.status_code == 400

        @patch('routes.providers.worker.redis_queue.enqueue_call')
        @clean_database
        def when_provider_is_not_offerer_or_venue(self, mock_add_to_redis_queue, app):
            # Given
            data = {'dossier_id': '666'}

            # When
            response = TestClient(app.test_client()).post('/providers/provider_name/application_update', form=data)

            # Then
            assert response.status_code == 400
