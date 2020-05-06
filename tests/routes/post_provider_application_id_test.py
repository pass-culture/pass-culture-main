from tests.conftest import clean_database, TestClient
from unittest.mock import call, patch
from workers.save_offerer_bank_informations import pc_synchronize_new_bank_informations

class Post:
    class Returns202:
        @patch('routes.providers.worker.redis_queue.enqueue_call')
        @clean_database
        def when_user_has_rights(self, mock_add_to_redis_queue, app):
            # Given
            data = {'dossier_id': '666'}

            # When
            response = TestClient(app.test_client()).post('/providers/provider_name/application_update', form=data)

            # Then
            assert response.status_code == 202
            assert mock_add_to_redis_queue.call_args_list == [
              call(func=pc_synchronize_new_bank_informations, args=('666', ))
            ]

    class Returns400:
        @patch('routes.providers.worker.redis_queue.enqueue_call')
        @clean_database
        def when_user_has_rights(self, mock_add_to_redis_queue, app):
            # Given
            data = {'fake_key': '666'}

            # When
            response = TestClient(app.test_client()).post('/providers/provider_name/application_update', form=data)

            # Then
            assert response.status_code == 400

