import pytest
from datetime import datetime
from freezegun import freeze_time
from unittest.mock import patch

from models.pc_object import serialize
from models.user import User
from tests.conftest import clean_database, TestClient
from tests.test_utils import API_URL, req

BASE_DATA = {
    'email': 'toto@btmx.fr',
    'firstName': 'Toto',
    'lastName': 'Martin',
    'postalCode': '93100',
    'publicName': 'Toto',
    'password': '__v4l1d_P455sw0rd__',
    'contact_ok': 'true',
    'phoneNumber': '0612345678',
    'dateOfBirth': serialize(datetime(2001, 1, 1)),
}


@pytest.mark.standalone
class Post:
    class Returns201:
        @clean_database
        @freeze_time('2019-01-01 01:00:00')
        @clean_database
        def when_data_is_accurate(self, app):
            # Given
            data = BASE_DATA.copy()
            expected_response_json = {'canBookFreeOffers': False,
                                      'departementCode': '93',
                                      'email': 'toto@btmx.fr',
                                      'firstName': 'Toto',
                                      'firstThumbDominantColor': None,
                                      'isAdmin': False,
                                      'lastName': 'Martin',
                                      'modelName': 'User',
                                      'phoneNumber': '0612345678',
                                      'postalCode': '93100',
                                      'publicName': 'Toto',
                                      'thumbCount': 0,
                                      'wallet_balance': 0,
                                      'dateOfBirth': '2001-01-01T00:00:00Z'}
            other_expected_keys = {'id', 'dateCreated'}

            # When
            response = TestClient() \
                .post(API_URL + '/users/signup/webapp',
                                json=data, headers={'origin': 'http://localhost:3000'})

            # Then
            assert response.status_code == 201
            assert 'Set-Cookie' not in response.headers
            json = response.json()
            for key, value in expected_response_json.items():
                if key != 'dateCreated':
                    assert json[key] == value
            for key in other_expected_keys:
                assert key in json

        @clean_database
        def test_created_user_has_validation_token_and_cannot_book_free_offers(self, app):
            data = BASE_DATA.copy()

            # When
            response = TestClient() \
                .post(API_URL + '/users/signup/webapp',
                      json=data, headers={'origin': 'http://localhost:3000'})

            # Then
            assert response.status_code == 201
            assert 'validationToken' not in response.json()
            created_user = User.query.filter_by(email='toto@btmx.fr').first()
            assert created_user.validationToken is not None
            assert not created_user.canBookFreeOffers

        @clean_database
        def when_setting_is_admin_true_and_can_book_free_offers_true_creates_account_with_can_book_free_offers_false(self, app):
            # Given
            user_json = {
                'email': 'pctest.isAdmin.canBook@btmx.fr',
                'publicName': 'IsAdmin CanBook',
                'firstName': 'IsAdmin',
                'lastName': 'CanBook',
                'postalCode': '93100',
                'password': '__v4l1d_P455sw0rd__',
                'contact_ok': 'true',
                'isAdmin': True,
                'canBookFreeOffers': True
            }

            # When
            r_signup = TestClient() \
                .post(API_URL + '/users/signup/webapp',
                                json=user_json, headers={'origin': 'http://localhost:3000'})

            # Then
            assert r_signup.status_code == 201
            created_user = User.query.filter_by(email='pctest.isAdmin.canBook@btmx.fr').one()
            assert created_user.isAdmin
            assert not created_user.canBookFreeOffers


    class Returns400:
        @clean_database
        def when_email_missing(self, app):
            # Given
            data = BASE_DATA.copy()
            del (data['email'])

            # When
            r_signup = TestClient() \
                .post(API_URL + '/users/signup/webapp',
                                json=data, headers={'origin': 'http://localhost:3000'})

            # Then
            assert r_signup.status_code == 400
            error = r_signup.json()
            assert 'email' in error

        @clean_database
        def when_email_with_invalid_format(self, app):
            # Given
            data = BASE_DATA.copy()
            data['email'] = 'toto'

            # When
            r_signup = TestClient() \
                .post(API_URL + '/users/signup/webapp',
                                json=data, headers={'origin': 'http://localhost:3000'})

            # Then
            assert r_signup.status_code == 400
            error = r_signup.json()
            assert 'email' in error

        @clean_database
        def when_email_is_already_used(self, app):
            TestClient() \
                .post(API_URL + '/users/signup/webapp',
                     json=BASE_DATA, headers={'origin': 'http://localhost:3000'})

            # When
            r_signup = TestClient() \
                .post(API_URL + '/users/signup/webapp',
                                json=BASE_DATA, headers={'origin': 'http://localhost:3000'})

            # Then
            assert r_signup.status_code == 400
            error = r_signup.json()
            assert 'email' in error

        @clean_database
        def when_public_name_is_missing(self, app):
            # Given
            data = BASE_DATA.copy()
            del (data['publicName'])

            # When
            r_signup = TestClient() \
                .post(API_URL + '/users/signup/webapp',
                                json=data, headers={'origin': 'http://localhost:3000'})

            # Then
            assert r_signup.status_code == 400
            error = r_signup.json()
            assert 'publicName' in error

        @clean_database
        def when_public_name_is_too_short(self, app):
            # Given
            data = BASE_DATA.copy()
            data['publicName'] = 't'

            # When
            r_signup = TestClient() \
                .post(API_URL + '/users/signup/webapp',
                                json=data, headers={'origin': 'http://localhost:3000'})

            # Then
            assert r_signup.status_code == 400
            error = r_signup.json()
            assert 'publicName' in error

        @clean_database
        def when_public_name_is_too_long(self, app):
            # Given
            data = BASE_DATA.copy()
            data['publicName'] = 'x' * 32

            # When
            r_signup = TestClient() \
                .post(API_URL + '/users/signup/webapp',
                                json=data, headers={'origin': 'http://localhost:3000'})

            # Then
            assert r_signup.status_code == 400
            error = r_signup.json()
            assert 'publicName' in error

        @clean_database
        def when_password_is_missing(self, app):
            # Given
            data = BASE_DATA.copy()
            del (data['password'])

            # When
            r_signup = TestClient() \
                .post(API_URL + '/users/signup/webapp',
                                json=data, headers={'origin': 'http://localhost:3000'})

            # Then
            assert r_signup.status_code == 400
            error = r_signup.json()
            assert 'password' in error

        @clean_database
        def when_password_is_invalid(self, app):
            # Given
            data = BASE_DATA.copy()
            data['password'] = 'weakpassword'

            # When
            r_signup = TestClient() \
                .post(API_URL + '/users/signup/webapp',
                                json=data, headers={'origin': 'http://localhost:3000'})

            # Then
            assert r_signup.status_code == 400
            response = r_signup.json()
            assert response['password'] == [
                'Le mot de passe doit faire au moins 12 caractères et contenir à minima '
                '1 majuscule, 1 minuscule, 1 chiffre et 1 caractère spécial parmi _-&?~#|^@=+.$,<>%*!:;'
            ]

        @clean_database
        def when_missing_contact_ok(self, app):
            data = BASE_DATA.copy()
            del (data['contact_ok'])

            # When
            r_signup = TestClient() \
                .post(API_URL + '/users/signup/webapp',
                                json=data, headers={'origin': 'http://localhost:3000'})

            # Then
            assert r_signup.status_code == 400
            error = r_signup.json()
            assert 'contact_ok' in error

        @clean_database
        def when_wrong_format_on_contact_ok(self, app):
            data = BASE_DATA.copy()
            data['contact_ok'] = 't'

            # When
            r_signup = TestClient() \
                .post(API_URL + '/users/signup/webapp',
                                json=data, headers={'origin': 'http://localhost:3000'})

            # Then
            assert r_signup.status_code == 400
            error = r_signup.json()
            assert 'contact_ok' in error

        @clean_database
        @patch('connectors.google_spreadsheet.get_authorized_emails_and_dept_codes')
        def when_user_not_in_exp_spreadsheet(self, get_authorized_emails_and_dept_codes, app):
            # Given
            get_authorized_emails_and_dept_codes.return_value = (['toto@email.com', 'other@email.com'], ['93', '93'])
            data = BASE_DATA.copy()
            data['email'] = 'unknown@unknown.com'

            # When
            r_signup = TestClient() \
                .post(API_URL + '/users/signup/webapp',
                                json=data, headers={'origin': 'http://localhost:3000'})

            # Then
            assert r_signup.status_code == 400
            error = r_signup.json()
            assert 'email' in error
