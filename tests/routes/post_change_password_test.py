from models import UserSQLEntity
from repository import repository
from tests.conftest import clean_database, TestClient
from tests.model_creators.generic_creators import create_user


class PostChangePassword:
    class Returns200:
        @clean_database
        def when_current_user_changes_password(self, app):
            # given
            user = create_user(email='user@test.com')
            repository.save(user)
            data = {'oldPassword': user.clearTextPassword, 'newPassword': 'N3W_p4ssw0rd'}
            user_id = user.id

            # when
            response = TestClient(app.test_client()) \
                .with_auth(user.email).post('/users/current/change-password',
                                            json=data)

            # then
            user = UserSQLEntity.query.get(user_id)
            assert user.checkPassword('N3W_p4ssw0rd') is True
            assert response.status_code == 204

    class Returns400:
        @clean_database
        def when_old_password_is_missing(self, app):
            # given
            user = create_user(email='user@test.com')
            repository.save(user)
            data = {'newPassword': 'N3W_p4ssw0rd'}

            # when
            response = TestClient(app.test_client()) \
                .with_auth(user.email).post('/users/current/change-password',
                                            json=data)

            # then
            assert response.status_code == 400
            assert response.json['oldPassword'] == ['Ancien mot de passe manquant']

        @clean_database
        def when_new_password_is_missing(self, app):
            # given
            user = create_user(email='user@test.com')
            repository.save(user)
            data = {'oldPassword': '0ldp4ssw0rd'}

            # when
            response = TestClient(app.test_client()) \
                .with_auth(user.email).post('/users/current/change-password',
                                            json=data)

            # then
            assert response.status_code == 400
            assert response.json['newPassword'] == ['Nouveau mot de passe manquant']

        @clean_database
        def when_new_password_is_not_strong_enough(self, app):
            # given
            user = create_user(email='user@test.com')
            repository.save(user)
            data = {'oldPassword': '0ldp4ssw0rd', 'newPassword': 'weakpassword'}

            # when
            response = TestClient(app.test_client()) \
                .with_auth(user.email).post('/users/current/change-password',
                                            json=data)

            # then
            assert response.status_code == 400
            assert response.json['newPassword'] == [
                'Ton mot de passe doit contenir au moins :\n'
                '- 12 caractères\n'
                '- Un chiffre\n'
                '- Une majuscule et une minuscule\n'
                '- Un caractère spécial'
            ]
