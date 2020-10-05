from datetime import datetime, timedelta

from models import UserSQLEntity
from repository import repository
import pytest
from tests.conftest import TestClient
from tests.model_creators.generic_creators import create_user


class PostNewPassword:
    class Returns400:
        @pytest.mark.usefixtures("db_session")
        def when_the_token_is_outdated(self, app):
            # given
            user = create_user(reset_password_token='KL89PBNG51',
                               reset_password_token_validity_limit=datetime.utcnow() - timedelta(days=2))
            repository.save(user)

            data = {
                'token': 'KL89PBNG51',
                'newPassword': 'N3W_p4ssw0rd'
            }

            # when
            response = TestClient(app.test_client()).post('/users/new-password', json=data,
                                                          headers={'origin': 'http://localhost:3000'})

            # then
            assert response.status_code == 400
            assert response.json['token'] == [
                'Votre lien de changement de mot de passe est périmé. Veuillez effectuer une nouvelle demande.'
            ]

        @pytest.mark.usefixtures("db_session")
        def when_the_token_is_unknown(self, app):
            # given
            user = create_user(reset_password_token='KL89PBNG51')
            repository.save(user)

            data = {
                'token': 'AZER1QSDF2',
                'newPassword': 'N3W_p4ssw0rd'
            }

            # when
            response = TestClient(app.test_client()).post('/users/new-password', json=data,
                                                          headers={'origin': 'http://localhost:3000'})

            # then
            assert response.status_code == 400
            assert response.json['token'] == [
                'Votre lien de changement de mot de passe est invalide.'
            ]

        @pytest.mark.usefixtures("db_session")
        def when_the_token_is_missing(self, app):
            # given
            user = create_user(reset_password_token='KL89PBNG51')
            repository.save(user)

            data = {'newPassword': 'N3W_p4ssw0rd'}

            # when
            response = TestClient(app.test_client()).post('/users/new-password', json=data,
                                                          headers={'origin': 'http://localhost:3000'})

            # then
            assert response.status_code == 400
            assert response.json['token'] == [
                'Votre lien de changement de mot de passe est invalide.'
            ]

        @pytest.mark.usefixtures("db_session")
        def when_new_password_is_missing(self, app):
            # given
            user = create_user(reset_password_token='KL89PBNG51')
            repository.save(user)

            data = {'token': 'KL89PBNG51'}

            # when
            response = TestClient(app.test_client()).post('/users/new-password', json=data,
                                                          headers={'origin': 'http://localhost:3000'})

            # then
            assert response.status_code == 400
            assert response.json['newPassword'] == [
                'Vous devez renseigner un nouveau mot de passe.'
            ]

        @pytest.mark.usefixtures("db_session")
        def when_new_password_is_not_strong_enough(self, app):
            # given
            user = create_user(reset_password_token='KL89PBNG51', reset_password_token_validity_limit=datetime.utcnow() + timedelta(hours=24))
            repository.save(user)

            data = {'token': 'KL89PBNG51', 'newPassword': 'weak_password'}

            # when
            response = TestClient(app.test_client()).post('/users/new-password', json=data,
                                                          headers={'origin': 'http://localhost:3000'})

            # then
            assert response.status_code == 400
            assert response.json['newPassword'] == [
                'Ton mot de passe doit contenir au moins :\n'
                '- 12 caractères\n'
                '- Un chiffre\n'
                '- Une majuscule et une minuscule\n'
                '- Un caractère spécial'
            ]

    class Returns204:
        @pytest.mark.usefixtures("db_session")
        def when_new_password_is_valid(self, app):
            # given
            user = create_user(reset_password_token='KL89PBNG51', reset_password_token_validity_limit=datetime.utcnow() + timedelta(hours=24))
            repository.save(user)
            user_id = user.id
            data = {
                'token': 'KL89PBNG51',
                'newPassword': 'N3W_p4ssw0rd'
            }

            # when
            response = TestClient(app.test_client()).post('/users/new-password', json=data,
                                                          headers={'origin': 'http://localhost:3000'})

            # then
            user = UserSQLEntity.query.get(user_id)
            assert response.status_code == 204
            assert user.checkPassword('N3W_p4ssw0rd')
            assert user.resetPasswordToken is None
            assert user.resetPasswordTokenValidityLimit is None
