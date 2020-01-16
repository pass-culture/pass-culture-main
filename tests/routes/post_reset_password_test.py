from datetime import datetime, timedelta
from unittest.mock import patch

from domain.password import RESET_PASSWORD_TOKEN_LENGTH
from models import User
from repository.repository import Repository
from tests.conftest import clean_database, TestClient
from tests.model_creators.generic_creators import create_user


class PostResetPassword:
    class Returns400:
        @clean_database
        def when_email_is_empty(self, app):
            # given
            data = {'email': ''}

            # when
            response = TestClient(app.test_client()).post('/users/reset-password', json=data,
                                                          headers={'origin': 'http://localhost:3000'})

            # then
            assert response.status_code == 400
            assert response.json['email'] == ['L\'email renseigné est vide']

        @clean_database
        def when_email_is_missing(self, app):
            # given
            data = {}

            # when
            response = TestClient(app.test_client()).post('/users/reset-password', json=data,
                                                          headers={'origin': 'http://localhost:3000'})

            # then
            assert response.status_code == 400
            assert response.json['email'] == ['L\'email est manquant']

    class Returns204:
        @clean_database
        def when_user_email_is_unknown(self, app):
            # given
            data = {'email': 'unknown.user@test.com'}

            # when
            response = TestClient(app.test_client()).post('/users/reset-password', json=data,
                                                          headers={'origin': 'http://localhost:3000'})

            # then
            assert response.status_code == 204

        @clean_database
        def when_email_is_known(self, app):
            # given
            data = {'email': 'bobby@test.com'}
            user = create_user(email='bobby@test.com')
            Repository.save(user)
            user_id = user.id

            # when
            response = TestClient(app.test_client()).post('/users/reset-password', json=data,
                                                          headers={'origin': 'http://localhost:3000'})

            # then
            user = User.query.get(user_id)
            assert response.status_code == 204
            assert len(user.resetPasswordToken) == RESET_PASSWORD_TOKEN_LENGTH
            now = datetime.utcnow()
            assert (now + timedelta(hours=23)) < user.resetPasswordTokenValidityLimit < (now + timedelta(hours=25))

        @clean_database
        @patch('routes.passwords.send_reset_password_email_with_mailjet_template')
        @patch('routes.passwords.send_raw_email')
        def test_should_send_reset_password_with_mailjet_template_when_user_is_a_beneficiary(self, send_raw_email_mock,
                                                                                             send_reset_password_email_with_mailjet_template_mock,
                                                                                             app):
            # given
            data = {'email': 'bobby@example.com'}
            user = create_user(can_book_free_offers=True, email='bobby@example.com')
            app_origin_header = 'http://localhost:3000'
            Repository.save(user)

            # when
            TestClient(app.test_client()).post('/users/reset-password', json=data,
                                                          headers={'origin': app_origin_header})

            # then
            send_reset_password_email_with_mailjet_template_mock.assert_called_once_with(user, send_raw_email_mock)

        @clean_database
        @patch('routes.passwords.send_reset_password_email')
        @patch('routes.passwords.send_raw_email')
        def test_should_send_reset_password_when_user_is_an_offerer(self, send_raw_email_mock, send_reset_password_email_mock, app):
            # given
            data = {'email': 'bobby@example.com'}
            user = create_user(can_book_free_offers=False, email='bobby@example.com')
            app_origin_header = 'http://localhost:3000'
            Repository.save(user)

            # when
            TestClient(app.test_client()).post('/users/reset-password', json=data,
                                                          headers={'origin': app_origin_header})

            # then
            send_reset_password_email_mock.assert_called_once_with(user, send_raw_email_mock, app_origin_header)
