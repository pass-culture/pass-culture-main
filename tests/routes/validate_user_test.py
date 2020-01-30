from unittest.mock import patch

from models import User, Offerer, UserOfferer
from repository import repository
from tests.conftest import clean_database, TestClient
from tests.model_creators.generic_creators import create_user, create_offerer, create_user_offerer


class Patch:
    class Returns204:
        @clean_database
        def expect_validation_token_to_be_set_to_none(self, app):
            # Given
            user = create_user()
            user.generate_validation_token()
            repository.save(user)
            user_id = user.id

            # When
            response = TestClient(app.test_client()) \
                .patch(f'/validate/user/{user.validationToken}', headers={'origin': 'http://localhost:3000'})

            # Then
            assert response.status_code == 204
            assert User.query.get(user_id).isValidated

        @clean_database
        @patch('routes.validate.send_ongoing_offerer_attachment_information_email_to_pro',
               return_value=True)
        @patch('routes.validate.send_raw_email', return_value=True)
        def test_send_ongoing_offerer_attachment_information_email_to_pro(self,
                                                                          mock_send_raw_email,
                                                                          mock_send_ongoing_offerer_attachment_information_email_to_pro,
                                                                          app):
            # Given
            user = create_user()
            user2 = create_user(email='pro2@example.com')
            offerer = create_offerer()
            user_offerer = create_user_offerer(user, offerer)
            user_offerer2 = create_user_offerer(user2, offerer)

            user.generate_validation_token()

            repository.save(user_offerer, user_offerer2)

            # When
            response = TestClient(app.test_client()) \
                .patch(f'/validate/user/{user.validationToken}', headers={'origin': 'http://localhost:3000'})

            # Then
            assert response.status_code == 204
            mock_send_ongoing_offerer_attachment_information_email_to_pro.assert_called_once_with(user_offerer,
                                                                                                  mock_send_raw_email)

        @clean_database
        @patch('routes.validate.send_pro_user_waiting_for_validation_by_admin_email',
               return_value=True)
        @patch('routes.validate.send_raw_email', return_value=True)
        def test_send_pro_user_waiting_for_validation_by_admin_email(self,
                                                                     mock_send_raw_email,
                                                                     mock_send_pro_user_waiting_for_validation_by_admin_email,
                                                                     app):
            # Given
            user = create_user()
            offerer = create_offerer()
            user_offerer = create_user_offerer(user, offerer)

            user.generate_validation_token()

            repository.save(user_offerer)

            # When
            response = TestClient(app.test_client()) \
                .patch(f'/validate/user/{user.validationToken}', headers={'origin': 'http://localhost:3000'})

            # Then
            assert response.status_code == 204
            mock_send_pro_user_waiting_for_validation_by_admin_email.assert_called_once_with(user, mock_send_raw_email,
                                                                                             offerer)

        @clean_database
        @patch('routes.validate.IS_INTEGRATION', False)
        @patch('routes.validate.maybe_send_offerer_validation_email',
               return_value=True)
        @patch('routes.validate.send_raw_email', return_value=True)
        def test_maybe_send_offerer_validation_email_when_not_in_integration_env(self,
                                                                                 mock_send_raw_email,
                                                                                 mock_maybe_send_offerer_validation_email,
                                                                                 app):
            # Given
            pro = create_user()
            offerer = create_offerer(siren='775671464')
            user_offerer = create_user_offerer(pro, offerer)

            pro.generate_validation_token()

            repository.save(user_offerer)

            # When
            response = TestClient(app.test_client()) \
                .patch(f'/validate/user/{pro.validationToken}', headers={'origin': 'http://localhost:3000'})

            # Then
            assert response.status_code == 204
            mock_maybe_send_offerer_validation_email.assert_called_once_with(offerer, user_offerer, mock_send_raw_email)

        @clean_database
        @patch('routes.validate.IS_INTEGRATION', True)
        @patch('routes.validate.maybe_send_offerer_validation_email',
               return_value=True)
        def test_validate_offerer_and_user_offerer_when_in_integration_env(self,
                                                                           mock_maybe_send_offerer_validation_email,
                                                                           app):
            # Given
            pro = create_user()
            offerer = create_offerer()
            user_offerer = create_user_offerer(pro, offerer)

            pro.generate_validation_token()

            repository.save(user_offerer)

            # When
            response = TestClient(app.test_client()) \
                .patch(f'/validate/user/{pro.validationToken}', headers={'origin': 'http://localhost:3000'})

            # Then
            assert response.status_code == 204
            assert mock_maybe_send_offerer_validation_email.call_count == 0
            offerer = Offerer.query.first()
            user_offerer = UserOfferer.query.first()
            assert offerer.validationToken is None
            assert user_offerer.validationToken is None


class Returns404:
    @clean_database
    def when_validation_token_is_not_found(self, app):
        # Given
        random_token = '0987TYGHHJMJ'

        # When
        response = TestClient(app.test_client()) \
            .patch(f'/validate/user/{random_token}', headers={'origin': 'http://localhost:3000'})

        # Then
        assert response.status_code == 404
        assert response.json['global'] == ['Ce lien est invalide']
