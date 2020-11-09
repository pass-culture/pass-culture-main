import pytest

from pcapi.model_creators.generic_creators import create_user
from pcapi.models import UserSession
from pcapi.repository import repository

from tests.conftest import TestClient


class Post:
    class Returns200:
        @pytest.mark.usefixtures("db_session")
        def when_account_is_known(self, app):
            # given
            user = create_user(email='user@example.com')
            repository.save(user)
            data = {'identifier': user.email, 'password': user.clearTextPassword}

            # when
            response = TestClient(app.test_client()).post('/beneficiaries/signin', json=data)

            # then
            assert response.status_code == 200

        @pytest.mark.usefixtures("db_session")
        def when_account_is_known_with_mixed_case_email(self, app):
            # given
            user = create_user(email='USER@example.COM')
            repository.save(user)
            data = {'identifier': 'uSeR@EXAmplE.cOm', 'password': user.clearTextPassword}

            # when
            response = TestClient(app.test_client()).post('/beneficiaries/signin', json=data)

            # then
            assert response.status_code == 200

        @pytest.mark.usefixtures("db_session")
        def when_account_is_known_with_trailing_spaces_in_email(self, app):
            # given
            user = create_user(email='user@example.com')
            repository.save(user)
            data = {'identifier': '  user@example.com  ', 'password': user.clearTextPassword}

            # when
            response = TestClient(app.test_client()).post('/beneficiaries/signin', json=data)

            # then
            assert response.status_code == 200

        @pytest.mark.usefixtures("db_session")
        def expect_a_new_user_session_to_be_recorded(self, app):
            # given
            user = create_user(email='user@example.com')
            repository.save(user)
            data = {'identifier': user.email, 'password': user.clearTextPassword}

            # when
            response = TestClient(app.test_client()).post('/beneficiaries/signin', json=data,
                                                          headers={'origin': 'http://localhost:3000'})

            # then
            assert response.status_code == 200

            session = UserSession.query.filter_by(userId=user.id).first()
            assert session is not None

    class Returns401:
        @pytest.mark.usefixtures("db_session")
        def when_identifier_is_missing(self, app):
            # Given
            user = create_user()
            repository.save(user)
            data = {'identifier': None, 'password': user.clearTextPassword}

            # When
            response = TestClient(app.test_client()).post('/beneficiaries/signin', json=data)

            # Then
            assert response.status_code == 401
            assert response.json['identifier'] == ['Identifiant manquant']

        @pytest.mark.usefixtures("db_session")
        def when_identifier_is_incorrect(self, app):
            # Given
            user = create_user()
            repository.save(user)
            data = {'identifier': 'random.email@test.com', 'password': user.clearTextPassword}

            # When
            response = TestClient(app.test_client()).post('/beneficiaries/signin', json=data)

            # Then
            assert response.status_code == 401
            assert response.json['identifier'] == ['Identifiant incorrect']

        @pytest.mark.usefixtures("db_session")
        def when_password_is_missing(self, app):
            # Given
            user = create_user()
            repository.save(user)
            data = {'identifier': user.email, 'password': None}

            # When
            response = TestClient(app.test_client()).post('/beneficiaries/signin', json=data)

            # Then
            assert response.status_code == 401
            assert response.json['password'] == ['Mot de passe manquant']

        @pytest.mark.usefixtures("db_session")
        def when_password_is_incorrect(self, app):
            # Given
            user = create_user()
            repository.save(user)
            data = {'identifier': user.email, 'password': 'wr0ng_p455w0rd'}

            # When
            response = TestClient(app.test_client()).post('/beneficiaries/signin', json=data)

            # Then
            assert response.status_code == 401
            assert response.json['password'] == ['Mot de passe incorrect']

        @pytest.mark.usefixtures("db_session")
        def when_account_is_not_validated(self, app):
            # Given
            user = create_user()
            user.generate_validation_token()
            repository.save(user)
            data = {'identifier': user.email, 'password': user.clearTextPassword}

            # When
            response = TestClient(app.test_client()).post('/beneficiaries/signin', json=data)

            # Then
            assert response.status_code == 401
            assert response.json['identifier'] == ['Ce compte n\'est pas validé.']
