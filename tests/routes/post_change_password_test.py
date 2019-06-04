from models import PcObject
from models.db import db
from tests.conftest import clean_database, TestClient
from tests.test_utils import API_URL, create_user


class PostChangePassword:
    class Returns200:
        @clean_database
        def when_current_user_changes_password(self, app):
            # given
            user = create_user(email='user@test.com')
            PcObject.save(user)
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
            PcObject.save(user)
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
            PcObject.save(user)
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
            PcObject.save(user)
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
