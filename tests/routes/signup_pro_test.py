from models.offerer import Offerer
from models.user_sql_entity import UserSQLEntity
from models.user_offerer import UserOfferer, RightsType
from repository import repository
from tests.conftest import clean_database, TestClient
from tests.model_creators.generic_creators import create_user, create_user_offerer

BASE_DATA_PRO = {
    'email': 'toto_pro@btmx.fr',
    'publicName': 'Toto Pro',
    'firstName': 'Toto',
    'lastName': 'Pro',
    'password': '__v4l1d_P455sw0rd__',
    'contact_ok': 'true',
    'siren': '349974931',
    'address': '12 boulevard de Pesaro',
    'phoneNumber': '0102030405',
    'postalCode': '92000',
    'city': 'Nanterre',
    'name': 'Crédit Coopératif',
}


class Post:
    class Returns201:
        @clean_database
        def when_user_data_is_valid(self, app):
            # Given
            data = BASE_DATA_PRO.copy()
            expected_response_json = {
                'canBookFreeOffers': False,
                'departementCode': '92',
                'email': 'toto_pro@btmx.fr',
                'firstName': 'Toto',
                'isAdmin': False,
                'lastName': 'Pro',
                'phoneNumber': '0102030405',
                'postalCode': '92000',
                'publicName': 'Toto Pro',
                'wallet_balance': 0,
                'dateOfBirth': None
            }
            other_expected_keys = {'id', 'dateCreated'}

            # When
            response = TestClient(app.test_client()) \
                .post('/users/signup/pro',
                      json=data, headers={'origin': 'http://localhost:3000'})

            # Then
            assert response.status_code == 201
            assert 'Set-Cookie' not in response.headers

            json = response.json
            assert 'dateCreated' in json
            for key, value in expected_response_json.items():
                if key != 'dateCreated':
                    assert json[key] == value
            for key in other_expected_keys:
                assert key in json

        @clean_database
        def test_does_not_allow_the_creation_of_admins(self, app):
            # Given
            user_json = {
                'email': 'toto_pro@btmx.fr',
                'publicName': 'Toto Pro',
                'firstName': 'Toto',
                'lastName': 'Pro',
                'password': '__v4l1d_P455sw0rd__',
                'contact_ok': 'true',
                'siren': '349974931',
                'address': '12 boulevard de Pesaro',
                'phoneNumber': '0102030405',
                'postalCode': '92000',
                'city': 'Nanterre',
                'name': 'Crédit Coopératif',
                'isAdmin': True
            }

            # When
            response = TestClient(app.test_client()) \
                .post('/users/signup/pro',
                      json=user_json, headers={'origin': 'http://localhost:3000'})

            # Then
            assert response.status_code == 201
            created_user = UserSQLEntity.query.filter_by(email='toto_pro@btmx.fr').one()
            assert not created_user.isAdmin

        @clean_database
        def test_creates_user_offerer_digital_venue_and_userOfferer_and_does_not_log_user_in(
                self, app):
            # Given
            data_pro = BASE_DATA_PRO.copy()

            # When
            response = TestClient(app.test_client()) \
                .post('/users/signup/pro',
                      json=data_pro, headers={'origin': 'http://localhost:3000'})

            # Then
            assert response.status_code == 201
            assert 'Set-Cookie' not in response.headers
            user = UserSQLEntity.query \
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
        def when_successful_and_existing_offerer_creates_editor_user_offerer_and_does_not_log_in(
                self, app):
            # Given
            json_offerer = {
                "name": "Test Offerer",
                "siren": "349974931",
                "address": "Test adresse",
                "postalCode": "75000",
                "city": "Paris"
            }
            offerer = Offerer(from_dict=json_offerer)
            offerer.generate_validation_token()
            user = create_user(email='bobby@test.com', public_name='bobby')
            user_offerer = create_user_offerer(user, offerer, is_admin=False)
            repository.save(offerer, user_offerer)

            data = BASE_DATA_PRO.copy()

            # When
            response = TestClient(app.test_client()) \
                .post('/users/signup/pro',
                      json=data, headers={'origin': 'http://localhost:3000'})

            # Then
            assert response.status_code == 201
            assert 'Set-Cookie' not in response.headers
            user = UserSQLEntity.query \
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
        def when_successful_and_existing_offerer_but_no_user_offerer_does_not_signin(self,
                                                                                     app):
            # Given
            json_offerer = {
                "name": "Test Offerer",
                "siren": "349974931",
                "address": "Test adresse",
                "postalCode": "75000",
                "city": "Paris"
            }
            offerer = Offerer(from_dict=json_offerer)
            repository.save(offerer)

            data = BASE_DATA_PRO.copy()

            # When
            response = TestClient(app.test_client()) \
                .post('/users/signup/pro',
                      json=data, headers={'origin': 'http://localhost:3000'})

            # Then
            assert response.status_code == 201
            assert 'Set-Cookie' not in response.headers
            user = UserSQLEntity.query \
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
        def when_successful_and_mark_pro_user_as_no_cultural_survey_needed(self,
                                                                           app):
            # Given
            json_offerer = {
                "name": "Test Offerer",
                "siren": "349974931",
                "address": "Test adresse",
                "postalCode": "75000",
                "city": "Paris"
            }
            offerer = Offerer(from_dict=json_offerer)
            repository.save(offerer)

            data = BASE_DATA_PRO.copy()

            # When
            response = TestClient(app.test_client()) \
                .post('/users/signup/pro',
                      json=data, headers={'origin': 'http://localhost:3000'})

            # Then
            assert response.status_code == 201
            user = UserSQLEntity.query \
                .filter_by(email='toto_pro@btmx.fr') \
                .first()
            assert user.needsToFillCulturalSurvey == False

    class Returns400:
        @clean_database
        def when_email_is_missing(self, app):
            # Given
            data = BASE_DATA_PRO.copy()
            del (data['email'])

            # When
            response = TestClient(app.test_client()) \
                .post('/users/signup/pro',
                      json=data, headers={'origin': 'http://localhost:3000'})

            # Then
            assert response.status_code == 400
            error = response.json
            assert 'email' in error

        @clean_database
        def when_email_is_invalid(self, app):
            # Given
            data = BASE_DATA_PRO.copy()
            data['email'] = 'toto'

            # When
            response = TestClient(app.test_client()) \
                .post('/users/signup/pro',
                      json=data, headers={'origin': 'http://localhost:3000'})

            # Then
            assert response.status_code == 400
            error = response.json
            assert 'email' in error

        @clean_database
        def when_email_is_already_used(self, app):
            # Given
            data = BASE_DATA_PRO.copy()
            TestClient(app.test_client()) \
                .post('/users/signup/pro',
                      json=data, headers={'origin': 'http://localhost:3000'})

            # When
            response = TestClient(app.test_client()) \
                .post('/users/signup/pro',
                      json=data, headers={'origin': 'http://localhost:3000'})

            # Then
            assert response.status_code == 400
            error = response.json
            assert 'email' in error

        @clean_database
        def when_public_name_is_missing(self, app):
            # Given
            data = BASE_DATA_PRO.copy()
            del (data['publicName'])

            # When
            response = TestClient(app.test_client()) \
                .post('/users/signup/pro',
                      json=data, headers={'origin': 'http://localhost:3000'})

            # Then
            assert response.status_code == 400
            error = response.json
            assert 'publicName' in error

        @clean_database
        def when_public_name_is_too_short(self, app):
            # Given
            data = BASE_DATA_PRO.copy()
            data['publicName'] = 't'

            # When
            response = TestClient(app.test_client()) \
                .post('/users/signup/pro',
                      json=data, headers={'origin': 'http://localhost:3000'})

            # Then
            assert response.status_code == 400
            error = response.json
            assert 'publicName' in error

        @clean_database
        def when_public_name_is_too_long(self, app):
            # Given
            data = BASE_DATA_PRO.copy()
            data['publicName'] = 'x' * 300

            # When
            response = TestClient(app.test_client()) \
                .post('/users/signup/pro',
                      json=data, headers={'origin': 'http://localhost:3000'})

            # Then
            assert response.status_code == 400
            error = response.json
            assert 'publicName' in error

        @clean_database
        def when_password_is_missing(self, app):
            # Given
            data = BASE_DATA_PRO.copy()
            del (data['password'])

            # When
            response = TestClient(app.test_client()) \
                .post('/users/signup/pro',
                      json=data, headers={'origin': 'http://localhost:3000'})

            # Then
            assert response.status_code == 400
            error = response.json
            assert 'password' in error

        @clean_database
        def when_password_is_invalid(self, app):
            # Given
            data = BASE_DATA_PRO.copy()
            data['password'] = 'weakpassword'

            # When
            response = TestClient(app.test_client()) \
                .post('/users/signup/pro',
                      json=data, headers={'origin': 'http://localhost:3000'})

            # Then
            assert response.status_code == 400
            response = response.json
            assert response['password'] == [
                'Le mot de passe doit faire au moins 12 caractères et contenir à minima '
                '1 majuscule, 1 minuscule, 1 chiffre et 1 caractère spécial parmi _-&?~#|^@=+.$,<>%*!:;'
            ]

        @clean_database
        def when_contact_ok_is_missing(self, app):
            # Given
            data = BASE_DATA_PRO.copy()
            del (data['contact_ok'])

            # When
            response = TestClient(app.test_client()) \
                .post('/users/signup/pro',
                      json=data, headers={'origin': 'http://localhost:3000'})

            # Then
            assert response.status_code == 400
            error = response.json
            assert 'contact_ok' in error

        @clean_database
        def when_contact_ok_format_is_invalid(self, app):
            # Given
            data = BASE_DATA_PRO.copy()
            data['contact_ok'] = 't'

            # When
            response = TestClient(app.test_client()) \
                .post('/users/signup/pro',
                      json=data, headers={'origin': 'http://localhost:3000'})

            # Then
            assert response.status_code == 400
            error = response.json
            assert 'contact_ok' in error

        @clean_database
        def when_offerer_name_is_missing(self, app):
            # Given
            data = BASE_DATA_PRO.copy()
            del (data['name'])

            # When
            response = TestClient(app.test_client()) \
                .post('/users/signup/pro',
                      json=data, headers={'origin': 'http://localhost:3000'})

            # Then
            assert response.status_code == 400
            error = response.json
            assert 'name' in error

        @clean_database
        def when_offerer_city_is_missing(self, app):
            # Given
            data = BASE_DATA_PRO.copy()
            del (data['city'])

            # When
            response = TestClient(app.test_client()) \
                .post('/users/signup/pro',
                      json=data, headers={'origin': 'http://localhost:3000'})

            # Then
            assert response.status_code == 400
            error = response.json
            assert 'city' in error

        @clean_database
        def when_postal_code_is_missing(self, app):
            # Given
            data = BASE_DATA_PRO.copy()
            del (data['postalCode'])

            # When
            response = TestClient(app.test_client()) \
                .post('/users/signup/pro',
                      json=data, headers={'origin': 'http://localhost:3000'})

            # Then
            assert response.status_code == 400
            error = response.json
            assert 'postalCode' in error

        @clean_database
        def when_invalid_postal_code(self, app):
            # Given
            data = BASE_DATA_PRO.copy()
            data['postalCode'] = '111'

            # When
            response = TestClient(app.test_client()) \
                .post('/users/signup/pro',
                      json=data, headers={'origin': 'http://localhost:3000'})

            # Then
            assert response.status_code == 400
            error = response.json
            assert 'postalCode' in error
