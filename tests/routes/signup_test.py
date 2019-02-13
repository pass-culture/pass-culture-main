from datetime import datetime
from unittest.mock import patch

import pytest
from freezegun import freeze_time

from models import PcObject
from models.offerer import Offerer
from models.pc_object import serialize
from models.user import User
from models.user_offerer import UserOfferer, RightsType
from tests.conftest import clean_database
from utils.test_utils import API_URL, req, create_user, create_user_offerer

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

BASE_DATA_PRO = {
    'email': 'toto_pro@btmx.fr',
    'publicName': 'Toto Pro',
    'firstName': 'Toto',
    'lastName': 'Pro',
    'password': '__v4l1d_P455sw0rd__',
    'contact_ok': 'true',
    'siren': '349974931',
    'address': '12 boulevard de Pesaro',
    'postalCode': '92000',
    'city': 'Nanterre',
    'name': 'Crédit Coopératif',

}


@pytest.mark.standalone
class WebappSignupTest:
    @clean_database
    def test_post_signup_webapp_create_user_with_validation_token(self, app):
        # Given
        user_data = BASE_DATA

        # When
        response = req.post(API_URL + '/users/signup/webapp', json=user_data,
                            headers={'origin': 'http://localhost:3000'})
        # Then
        created_user = User.query.filter_by(email=user_data['email']).first()
        assert 'validationToken' not in response.json()
        assert created_user.validationToken is not None

    @clean_database
    def test_signup_without_email_should_return_status_code_400_and_email_in_error(self, app):
        # Given
        data = BASE_DATA.copy()
        del (data['email'])

        # When
        r_signup = req.post(API_URL + '/users/signup/webapp',
                            json=data, headers={'origin': 'http://localhost:3000'})

        # Then
        assert r_signup.status_code == 400
        error = r_signup.json()
        assert 'email' in error

    @clean_database
    def test_signup_with_invalid_email_should_return_status_code_400_and_email_in_error(self, app):
        # Given
        data = BASE_DATA.copy()
        data['email'] = 'toto'

        # When
        r_signup = req.post(API_URL + '/users/signup/webapp',
                            json=data, headers={'origin': 'http://localhost:3000'})

        # Then
        assert r_signup.status_code == 400
        error = r_signup.json()
        assert 'email' in error

    @clean_database
    def test_signup_with_same_email_returns_status_code_400_and_email_in_error(self, app):
        req.post(API_URL + '/users/signup/webapp',
                 json=BASE_DATA, headers={'origin': 'http://localhost:3000'})

        # When
        r_signup = req.post(API_URL + '/users/signup/webapp',
                            json=BASE_DATA, headers={'origin': 'http://localhost:3000'})

        # Then
        assert r_signup.status_code == 400
        error = r_signup.json()
        assert 'email' in error

    @clean_database
    def test_signup_without_publicName_should_return_status_code_400_and_public_name_in_error(self, app):
        # Given
        data = BASE_DATA.copy()
        del (data['publicName'])

        # When
        r_signup = req.post(API_URL + '/users/signup/webapp',
                            json=data, headers={'origin': 'http://localhost:3000'})

        # Then
        assert r_signup.status_code == 400
        error = r_signup.json()
        assert 'publicName' in error

    @clean_database
    def test_signup_with_publicName_too_short_returns_status_code_400_and_public_name_in_error(self, app):
        # Given
        data = BASE_DATA.copy()
        data['publicName'] = 't'

        # When
        r_signup = req.post(API_URL + '/users/signup/webapp',
                            json=data, headers={'origin': 'http://localhost:3000'})

        # Then
        assert r_signup.status_code == 400
        error = r_signup.json()
        assert 'publicName' in error

    @clean_database
    def test_signup_with_publicName_too_long_returns_status_code_400_and_public_name_in_error(self, app):
        # Given
        data = BASE_DATA.copy()
        data['publicName'] = 'x' * 32

        # When
        r_signup = req.post(API_URL + '/users/signup/webapp',
                            json=data, headers={'origin': 'http://localhost:3000'})

        # Then
        assert r_signup.status_code == 400
        error = r_signup.json()
        assert 'publicName' in error

    @clean_database
    def test_signup_without_password_returns_status_code_400_and_password_in_error(self, app):
        # Given
        data = BASE_DATA.copy()
        del (data['password'])

        # When
        r_signup = req.post(API_URL + '/users/signup/webapp',
                            json=data, headers={'origin': 'http://localhost:3000'})

        # Then
        assert r_signup.status_code == 400
        error = r_signup.json()
        assert 'password' in error

    @clean_database
    def test_signup_with_invalid_password_returns_status_code_400_and_and_password_in_error(self, app):
        # Given
        data = BASE_DATA.copy()
        data['password'] = 'weakpassword'

        # When
        r_signup = req.post(API_URL + '/users/signup/webapp',
                            json=data, headers={'origin': 'http://localhost:3000'})

        # Then
        assert r_signup.status_code == 400
        response = r_signup.json()
        assert response['password'] == [
            'Le mot de passe doit faire au moins 12 caractères et contenir à minima '
            '1 majuscule, 1 minuscule, 1 chiffre et 1 caractère spécial parmi _-&?~#|^@=+.$,<>%*!:;'
        ]

    @clean_database
    def test_signup_without_contact_ok_returns_400_and_contact_ok_in_error(self, app):
        data = BASE_DATA.copy()
        del (data['contact_ok'])

        # When
        r_signup = req.post(API_URL + '/users/signup/webapp',
                            json=data, headers={'origin': 'http://localhost:3000'})

        # Then
        assert r_signup.status_code == 400
        error = r_signup.json()
        assert 'contact_ok' in error

    @clean_database
    def test_signup_with_invalid_contact_ok_returns_status_code_400_and_contact_ok_in_error(self, app):
        data = BASE_DATA.copy()
        data['contact_ok'] = 't'

        # When
        r_signup = req.post(API_URL + '/users/signup/webapp',
                            json=data, headers={'origin': 'http://localhost:3000'})

        # Then
        assert r_signup.status_code == 400
        error = r_signup.json()
        assert 'contact_ok' in error

    @freeze_time('2019-01-01 01:00:00')
    @clean_database
    def test_signup_successful_returns_status_code_201_and_does_not_log_user_in(self, app):
        # Given
        data = BASE_DATA.copy()
        expected_response_json = {'canBookFreeOffers': True,
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
        r_signup = req.post(API_URL + '/users/signup/webapp',
                            json=data, headers={'origin': 'http://localhost:3000'})

        # Then
        assert r_signup.status_code == 201
        assert 'Set-Cookie' not in r_signup.headers
        json = r_signup.json()
        for key, value in expected_response_json.items():
            if key != 'dateCreated':
                assert json[key] == value
        for key in other_expected_keys:
            assert key in json

    @clean_database
    @patch('connectors.google_spreadsheet.get_authorized_emails_and_dept_codes')
    def test_signup_when_user_not_in_exp_spreadsheet_returns_status_code_400_and_email_in_error(self,
                                                                                                get_authorized_emails_and_dept_codes,
                                                                                                app):
        # Given
        get_authorized_emails_and_dept_codes.return_value = (['toto@email.com', 'other@email.com'], ['93', '93'])
        data = BASE_DATA.copy()
        data['email'] = 'unknown@unknown.com'

        # When
        r_signup = req.post(API_URL + '/users/signup/webapp',
                            json=data, headers={'origin': 'http://localhost:3000'})

        # Then
        assert r_signup.status_code == 400
        error = r_signup.json()
        assert 'email' in error


@pytest.mark.standalone
class ProSignupTest:
    @clean_database
    def test_signup_without_email_should_return_status_code_400_and_email_in_error(self, app):
        # Given
        data = BASE_DATA_PRO.copy()
        del (data['email'])

        # When
        r_signup = req.post(API_URL + '/users/signup/pro',
                            json=data, headers={'origin': 'http://localhost:3000'})

        # Then
        assert r_signup.status_code == 400
        error = r_signup.json()
        assert 'email' in error

    @clean_database
    def test_signup_with_invalid_email_should_return_status_code_400_and_email_in_error(self, app):
        # Given
        data = BASE_DATA_PRO.copy()
        data['email'] = 'toto'

        # When
        r_signup = req.post(API_URL + '/users/signup/pro',
                            json=data, headers={'origin': 'http://localhost:3000'})

        # Then
        assert r_signup.status_code == 400
        error = r_signup.json()
        assert 'email' in error

    @clean_database
    def test_signup_with_same_email_returns_status_code_400_and_email_in_error(self, app):
        data = BASE_DATA_PRO.copy()
        req.post(API_URL + '/users/signup/pro',
                 json=data, headers={'origin': 'http://localhost:3000'})

        # When
        data['siren'] = '123456789'
        r_signup = req.post(API_URL + '/users/signup/pro',
                            json=data, headers={'origin': 'http://localhost:3000'})

        # Then
        assert r_signup.status_code == 400
        error = r_signup.json()
        assert 'email' in error

    @clean_database
    def test_signup_without_publicName_should_return_status_code_400_and_public_name_in_error(self, app):
        # Given
        data = BASE_DATA_PRO.copy()
        del (data['publicName'])

        # When
        r_signup = req.post(API_URL + '/users/signup/pro',
                            json=data, headers={'origin': 'http://localhost:3000'})

        # Then
        assert r_signup.status_code == 400
        error = r_signup.json()
        assert 'publicName' in error

    @clean_database
    def test_signup_with_publicName_too_short_returns_status_code_400_and_public_name_in_error(self, app):
        # Given
        data = BASE_DATA_PRO.copy()
        data['publicName'] = 't'

        # When
        r_signup = req.post(API_URL + '/users/signup/pro',
                            json=data, headers={'origin': 'http://localhost:3000'})

        # Then
        assert r_signup.status_code == 400
        error = r_signup.json()
        assert 'publicName' in error

    @clean_database
    def test_signup_with_publicName_too_long_returns_status_code_400_and_public_name_in_error(self, app):
        # Given
        data = BASE_DATA_PRO.copy()
        data['publicName'] = 'x' * 32

        # When
        r_signup = req.post(API_URL + '/users/signup/pro',
                            json=data, headers={'origin': 'http://localhost:3000'})

        # Then
        assert r_signup.status_code == 400
        error = r_signup.json()
        assert 'publicName' in error

    @clean_database
    def test_signup_without_password_returns_status_code_400_and_password_in_error(self, app):
        # Given
        data = BASE_DATA_PRO.copy()
        del (data['password'])

        # When
        r_signup = req.post(API_URL + '/users/signup/pro',
                            json=data, headers={'origin': 'http://localhost:3000'})

        # Then
        assert r_signup.status_code == 400
        error = r_signup.json()
        assert 'password' in error

    @clean_database
    def test_signup_with_invalid_password_returns_status_code_400_and_and_password_in_error(self, app):
        # Given
        data = BASE_DATA_PRO.copy()
        data['password'] = 'weakpassword'

        # When
        r_signup = req.post(API_URL + '/users/signup/pro',
                            json=data, headers={'origin': 'http://localhost:3000'})

        # Then
        assert r_signup.status_code == 400
        response = r_signup.json()
        assert response['password'] == [
            'Le mot de passe doit faire au moins 12 caractères et contenir à minima '
            '1 majuscule, 1 minuscule, 1 chiffre et 1 caractère spécial parmi _-&?~#|^@=+.$,<>%*!:;'
        ]

    @clean_database
    def test_signup_without_contact_ok_returns_status_code_400_and_contact_ok_in_error(self, app):
        data = BASE_DATA_PRO.copy()
        del (data['contact_ok'])

        # When
        r_signup = req.post(API_URL + '/users/signup/pro',
                            json=data, headers={'origin': 'http://localhost:3000'})

        # Then
        assert r_signup.status_code == 400
        error = r_signup.json()
        assert 'contact_ok' in error

    @clean_database
    def test_signup_with_invalid_contact_ok_returns_status_code_400_and_contact_ok_in_error(self, app):
        data = BASE_DATA_PRO.copy()
        data['contact_ok'] = 't'

        # When
        r_signup = req.post(API_URL + '/users/signup/pro',
                            json=data, headers={'origin': 'http://localhost:3000'})

        # Then
        assert r_signup.status_code == 400
        error = r_signup.json()
        assert 'contact_ok' in error

    @clean_database
    def test_signup_successful_returns_status_code_201_and_does_not_log_user_in(self, app):
        # Given
        data = BASE_DATA_PRO.copy()
        expected_response_json = {
            'canBookFreeOffers': False,
            'departementCode': '92',
            'email': 'toto_pro@btmx.fr',
            'firstName': 'Toto',
            'firstThumbDominantColor': None,
            'isAdmin': False,
            'lastName': 'Pro',
            'modelName': 'User',
            'phoneNumber': None,
            'postalCode': '92000',
            'publicName': 'Toto Pro',
            'thumbCount': 0,
            'wallet_balance': 0,
            'dateOfBirth': None
        }
        other_expected_keys = {'id', 'dateCreated'}

        # When
        r_signup = req.post(API_URL + '/users/signup/pro',
                            json=data, headers={'origin': 'http://localhost:3000'})

        # Then
        assert r_signup.status_code == 201
        assert 'Set-Cookie' not in r_signup.headers

        json = r_signup.json()
        assert 'dateCreated' in json
        for key, value in expected_response_json.items():
            if key != 'dateCreated':
                assert json[key] == value
        for key in other_expected_keys:
            assert key in json

    @clean_database
    def test_signup_without_offerer_name_returns_status_code_400_and_name_in_error(self, app):
        # Given
        data = BASE_DATA_PRO.copy()
        del (data['name'])

        # When
        r_signup = req.post(API_URL + '/users/signup/pro',
                            json=data, headers={'origin': 'http://localhost:3000'})

        # Then
        assert r_signup.status_code == 400
        error = r_signup.json()
        assert 'name' in error

    @clean_database
    def test_signup_without_offerer_city_returns_status_code_400_and_city_in_error(self, app):
        data = BASE_DATA_PRO.copy()
        del (data['city'])

        # When
        r_signup = req.post(API_URL + '/users/signup/pro',
                            json=data, headers={'origin': 'http://localhost:3000'})

        # Then
        assert r_signup.status_code == 400
        error = r_signup.json()
        assert 'city' in error

    @clean_database
    def test_signup_without_offerer_postal_code_returns_status_code_400_and_postal_code_in_error(self, app):
        data = BASE_DATA_PRO.copy()
        del (data['postalCode'])

        # When
        r_signup = req.post(API_URL + '/users/signup/pro',
                            json=data, headers={'origin': 'http://localhost:3000'})

        # Then
        assert r_signup.status_code == 400
        error = r_signup.json()
        assert 'postalCode' in error

    @clean_database
    def test_signup_with_invalid_offerer_postal_code_returns_status_code_400_and_postal_code_in_error(self, app):
        data = BASE_DATA_PRO.copy()
        data['postalCode'] = '111'

        # When
        r_signup = req.post(API_URL + '/users/signup/pro',
                            json=data, headers={'origin': 'http://localhost:3000'})

        # Then
        assert r_signup.status_code == 400
        error = r_signup.json()
        assert 'postalCode' in error

    @clean_database
    def test_pro_signup_when_successful_returns_status_code_201_creates_user_offerer_digital_venue_and_userOfferer_and_not_log_user_in(
            self, app):
        data_pro = BASE_DATA_PRO.copy()
        r_signup = req.post(API_URL + '/users/signup/pro',
                            json=data_pro, headers={'origin': 'http://localhost:3000'})
        assert r_signup.status_code == 201
        assert 'Set-Cookie' not in r_signup.headers
        user = User.query \
            .filter_by(email='toto_pro@btmx.fr') \
            .first()
        assert user is not None
        offerer = Offerer.query \
            .filter_by(siren='349974931') \
            .first()
        assert offerer is not None
        assert offerer.validationToken is not None
        assert len(offerer.managedVenues) == 1
        assert offerer.managedVenues[0].isVirtual
        user_offerer = UserOfferer.query \
            .filter_by(user=user,
                       offerer=offerer) \
            .first()
        assert user_offerer is not None
        assert user_offerer.validationToken is None
        assert user_offerer.rights == RightsType.editor

    @clean_database
    def test_pro_signup_when_existing_offerer_returns_status_code_201_creates_editor_user_offerer_and_does_not_log_in(
            self, app):
        json_offerer = {
            "name": "Test Offerer",
            "siren": "349974931",
            "address": "Test adresse",
            "postalCode": "75000",
            "city": "Paris"
        }
        offerer = Offerer(from_dict=json_offerer)
        offerer.generate_validation_token()
        user = create_user(public_name='bobby', email='bobby@test.com')
        user_offerer = create_user_offerer(user, offerer, is_admin=False)
        PcObject.check_and_save(offerer, user_offerer)

        data = BASE_DATA_PRO.copy()
        r_signup = req.post(API_URL + '/users/signup/pro',
                            json=data, headers={'origin': 'http://localhost:3000'})
        assert r_signup.status_code == 201
        assert 'Set-Cookie' not in r_signup.headers
        user = User.query \
            .filter_by(email='toto_pro@btmx.fr') \
            .first()
        assert user is not None
        offerer = Offerer.query \
            .filter_by(siren='349974931') \
            .first()
        assert offerer is not None
        user_offerer = UserOfferer.query \
            .filter_by(user=user, offerer=offerer) \
            .first()
        assert user_offerer is not None
        assert user_offerer.validationToken is not None
        assert user_offerer.rights == RightsType.editor

    @clean_database
    def test_pro_signup_when_existing_offerer_but_no_user_offerer_returns_status_code_201_and_does_not_signin(self,
                                                                                                              app):
        "should create user and userOfferer"
        json_offerer = {
            "name": "Test Offerer",
            "siren": "349974931",
            "address": "Test adresse",
            "postalCode": "75000",
            "city": "Paris"
        }
        offerer = Offerer(from_dict=json_offerer)
        PcObject.check_and_save(offerer)

        data = BASE_DATA_PRO.copy()
        r_signup = req.post(API_URL + '/users/signup/pro',
                            json=data, headers={'origin': 'http://localhost:3000'})
        assert r_signup.status_code == 201
        assert 'Set-Cookie' not in r_signup.headers
        user = User.query \
            .filter_by(email='toto_pro@btmx.fr') \
            .first()
        assert user is not None
        offerer = Offerer.query \
            .filter_by(siren='349974931') \
            .first()
        assert offerer is not None
        user_offerer = UserOfferer.query \
            .filter_by(user=user,
                       offerer=offerer) \
            .first()
        assert user_offerer is not None
        assert user_offerer.validationToken is not None
        assert user_offerer.rights == RightsType.editor

    @clean_database
    def test_signup_user_with_isAdmin_true_and_canBookFreeOffers_raises_error(self, app):
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
        r_signup = req.post(API_URL + '/users/signup/webapp',
                            json=user_json, headers={'origin': 'http://localhost:3000'})

        # Then
        assert r_signup.status_code == 400
        error = r_signup.json()
        assert error == {'canBookFreeOffers': ['Admin ne peut pas booker']}
