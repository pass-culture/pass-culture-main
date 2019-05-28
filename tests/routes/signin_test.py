import pytest

from models import PcObject
from tests.conftest import clean_database, TestClient
from tests.test_utils import API_URL, create_user


@pytest.mark.standalone
class Post:
    class Returns200:
        @clean_database
        def when_account_is_known(self, app):
            # given
            user = create_user(email='user@example.com')
            PcObject.save(user)
            data = {'identifier': user.email, 'password': user.clearTextPassword}

            # when
            response = TestClient().post(API_URL + '/users/signin', json=data)

            # then
            assert response.status_code == 200
            assert response.json()['expenses'] == {
                'all': {'actual': 0, 'max': 500},
                'digital': {'actual': 0, 'max': 200},
                'physical': {'actual': 0, 'max': 200}
            }

        @clean_database
        def when_account_is_known_with_mixed_case_email(self, app):
            # given
            user = create_user(email='USER@example.COM')
            PcObject.save(user)
            data = {'identifier': 'uSeR@EXAmplE.cOm', 'password': user.clearTextPassword}

            # when
            response = TestClient().post(API_URL + '/users/signin', json=data)

            # then
            assert response.status_code == 200

        @clean_database
        def when_account_is_known_with_trailing_spaces_in_email(self, app):
            # given
            user = create_user(email='user@example.com')
            PcObject.save(user)
            data = {'identifier': '  user@example.com  ', 'password': user.clearTextPassword}

            # when
            response = TestClient().post(API_URL + '/users/signin', json=data)

            # then
            assert response.status_code == 200

    class Returns401:
        @clean_database
        def when_identifier_is_missing(self, app):
            # Given
            user = create_user()
            PcObject.save(user)
            data = {'identifier': None, 'password': user.clearTextPassword}

            # When
            response = TestClient().post(API_URL + '/users/signin', json=data)

            # Then
            assert response.status_code == 401
            assert response.json()['identifier'] == ['Identifiant manquant']

        @clean_database
        def when_identifier_is_incorrect(self, app):
            # Given
            user = create_user()
            PcObject.save(user)
            data = {'identifier': 'random.email@test.com', 'password': user.clearTextPassword}

            # When
            response = TestClient().post(API_URL + '/users/signin', json=data)

            # Then
            assert response.status_code == 401
            assert response.json()['identifier'] == ['Identifiant incorrect']

        @clean_database
        def when_password_is_missing(self, app):
            # Given
            user = create_user()
            PcObject.save(user)
            data = {'identifier': user.email, 'password': None}

            # When
            response = TestClient().post(API_URL + '/users/signin', json=data)

            # Then
            assert response.status_code == 401
            assert response.json()['password'] == ['Mot de passe manquant']

        @clean_database
        def when_password_is_incorrect(self, app):
            # Given
            user = create_user()
            PcObject.save(user)
            data = {'identifier': user.email, 'password': 'wr0ng_p455w0rd'}

            # When
            response = TestClient().post(API_URL + '/users/signin', json=data)

            # Then
            assert response.status_code == 401
            assert response.json()['password'] == ['Mot de passe incorrect']

        @clean_database
        def when_account_is_not_validated(self, app):
            # Given
            user = create_user()
            user.generate_validation_token()
            PcObject.save(user)
            data = {'identifier': user.email, 'password': user.clearTextPassword}

            # When
            response = TestClient().post(API_URL + '/users/signin', json=data)

            # Then
            assert response.status_code == 401
            assert response.json()['identifier'] == ['Ce compte n\'est pas validé.']
