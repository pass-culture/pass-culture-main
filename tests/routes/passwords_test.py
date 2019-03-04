import pytest
from datetime import datetime, timedelta

from domain.password import RESET_PASSWORD_TOKEN_LENGTH
from models import PcObject
from models.db import db
from tests.conftest import clean_database, TestClient
from tests.test_utils import API_URL, create_user


@pytest.mark.standalone
class PostChangePassword:
    class Returns200:
        @clean_database
        def when_current_user_changes_password(self, app):
            # given
            user = create_user(email='user@test.com')
            PcObject.check_and_save(user)
            data = {'oldPassword': user.clearTextPassword, 'newPassword': 'N3W_p4ssw0rd'}

            # when
            response = TestClient() \
                .with_auth(user.email).post(API_URL + '/users/current/change-password',
                                            json=data)

            # then
            db.session.refresh(user)
            assert user.checkPassword('N3W_p4ssw0rd') is True
            assert response.status_code == 204

    class Returns400:
        @clean_database
        def when_old_password_is_missing(self, app):
            # given
            user = create_user(email='user@test.com')
            PcObject.check_and_save(user)
            data = {'newPassword': 'N3W_p4ssw0rd'}

            # when
            response = TestClient() \
                .with_auth(user.email).post(API_URL + '/users/current/change-password',
                                            json=data)

            # then
            assert response.status_code == 400
            assert response.json()['oldPassword'] == ['Ancien mot de passe manquant']

        @clean_database
        def when_new_password_is_missing(self, app):
            # given
            user = create_user(email='user@test.com')
            PcObject.check_and_save(user)
            data = {'oldPassword': '0ldp4ssw0rd'}

            # when
            response = TestClient() \
                .with_auth(user.email).post(API_URL + '/users/current/change-password',
                                            json=data)

            # then
            assert response.status_code == 400
            assert response.json()['newPassword'] == ['Nouveau mot de passe manquant']

        @clean_database
        def when_new_password_is_not_strong_enough(self, app):
            # given
            user = create_user(email='user@test.com')
            PcObject.check_and_save(user)
            data = {'oldPassword': '0ldp4ssw0rd', 'newPassword': 'weakpassword'}

            # when
            response = TestClient() \
                .with_auth(user.email).post(API_URL + '/users/current/change-password',
                                            json=data)

            # then
            assert response.status_code == 400
            assert response.json()['newPassword'] == [
                'Le mot de passe doit faire au moins 12 caractères et contenir à minima '
                '1 majuscule, 1 minuscule, 1 chiffre et 1 caractère spécial parmi _-&?~#|^@=+.$,<>%*!:;'
            ]


@pytest.mark.standalone
class PostResetPassword:
    class Returns400:
        @clean_database
        def when_email_is_empty(self, app):
            # given
            data = {'email': ''}

            # when
            response = TestClient().post(API_URL + '/users/reset-password', json=data,
                                         headers={'origin': 'http://localhost:3000'})

            # then
            assert response.status_code == 400
            assert response.json()['email'] == ['L\'email renseigné est vide']

        @clean_database
        def when_email_is_missing(self, app):
            # given
            data = {}

            # when
            response = TestClient().post(API_URL + '/users/reset-password', json=data,
                                         headers={'origin': 'http://localhost:3000'})

            # then
            assert response.status_code == 400
            assert response.json()['email'] == ['L\'email est manquant']

    class Returns204:
        @clean_database
        def when_user_email_is_unknown(self, app):
            # given
            data = {'email': 'unknown.user@test.com'}

            # when
            response = TestClient().post(API_URL + '/users/reset-password', json=data,
                                         headers={'origin': 'http://localhost:3000'})

            # then
            assert response.status_code == 204

        @clean_database
        def when_email_is_known(self, app):
            # given
            data = {'email': 'bobby@test.com'}
            user = create_user(email='bobby@test.com')
            PcObject.check_and_save(user)

            # when
            response = TestClient().post(API_URL + '/users/reset-password', json=data,
                                         headers={'origin': 'http://localhost:3000'})

            # then
            db.session.refresh(user)
            assert response.status_code == 204
            assert len(user.resetPasswordToken) == RESET_PASSWORD_TOKEN_LENGTH
            now = datetime.utcnow()
            assert (now + timedelta(hours=23)) < user.resetPasswordTokenValidityLimit < (now + timedelta(hours=25))


@pytest.mark.standalone
class PostNewPassword:
    class Returns400:
        @clean_database
        def when_the_token_is_outdated(self, app):
            # given
            user = create_user(reset_password_token='KL89PBNG51',
                               reset_password_token_validity_limit=datetime.utcnow() - timedelta(days=2))
            PcObject.check_and_save(user)

            data = {
                'token': 'KL89PBNG51',
                'newPassword': 'N3W_p4ssw0rd'
            }

            # when
            response = TestClient().post(API_URL + '/users/new-password', json=data,
                                         headers={'origin': 'http://localhost:3000'})

            # then
            assert response.status_code == 400
            assert response.json()['token'] == [
                'Votre lien de changement de mot de passe est périmé. Veuillez effecture une nouvelle demande.'
            ]

        @clean_database
        def when_the_token_is_unknown(self, app):
            # given
            user = create_user(reset_password_token='KL89PBNG51')
            PcObject.check_and_save(user)

            data = {
                'token': 'AZER1QSDF2',
                'newPassword': 'N3W_p4ssw0rd'
            }

            # when
            response = TestClient().post(API_URL + '/users/new-password', json=data,
                                         headers={'origin': 'http://localhost:3000'})

            # then
            assert response.status_code == 400
            assert response.json()['token'] == [
                'Votre lien de changement de mot de passe est invalide.'
            ]

        @clean_database
        def when_the_token_is_missing(self, app):
            # given
            user = create_user(reset_password_token='KL89PBNG51')
            PcObject.check_and_save(user)

            data = {'newPassword': 'N3W_p4ssw0rd'}

            # when
            response = TestClient().post(API_URL + '/users/new-password', json=data,
                                         headers={'origin': 'http://localhost:3000'})

            # then
            assert response.status_code == 400
            assert response.json()['token'] == [
                'Votre lien de changement de mot de passe est invalide.'
            ]

        @clean_database
        def when_new_password_is_missing(self, app):
            # given
            user = create_user(reset_password_token='KL89PBNG51')
            PcObject.check_and_save(user)

            data = {'token': 'KL89PBNG51'}

            # when
            response = TestClient().post(API_URL + '/users/new-password', json=data,
                                         headers={'origin': 'http://localhost:3000'})

            # then
            assert response.status_code == 400
            assert response.json()['newPassword'] == [
                'Vous devez renseigner un nouveau mot de passe.'
            ]

        @clean_database
        def when_new_password_is_not_strong_enough(self, app):
            # given
            user = create_user(reset_password_token='KL89PBNG51')
            PcObject.check_and_save(user)

            data = {'token': 'KL89PBNG51', 'newPassword': 'weak_password'}

            # when
            response = TestClient().post(API_URL + '/users/new-password', json=data,
                                         headers={'origin': 'http://localhost:3000'})

            # then
            assert response.status_code == 400
            assert response.json()['newPassword'] == [
                'Le mot de passe doit faire au moins 12 caractères et contenir à minima '
                '1 majuscule, 1 minuscule, 1 chiffre et 1 caractère spécial parmi _-&?~#|^@=+.$,<>%*!:;'
            ]

    class Returns204:
        @clean_database
        def when_new_password_is_valid(self, app):
            # given
            user = create_user(reset_password_token='KL89PBNG51')
            PcObject.check_and_save(user)

            data = {
                'token': 'KL89PBNG51',
                'newPassword': 'N3W_p4ssw0rd'
            }

            # when
            response = TestClient().post(API_URL + '/users/new-password', json=data,
                                         headers={'origin': 'http://localhost:3000'})

            # then
            db.session.refresh(user)
            assert response.status_code == 204
            assert user.checkPassword('N3W_p4ssw0rd')
            assert user.resetPasswordToken is None
            assert user.resetPasswordTokenValidityLimit is None
