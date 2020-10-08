import copy
from unittest.mock import patch, MagicMock

from models import Offerer, RightsType, UserOfferer
from repository import repository
import pytest
from tests.conftest import TestClient
from model_creators.generic_creators import create_user, create_offerer, create_user_offerer, create_venue_type
from utils.human_ids import humanize

api_entreprise_json_mock = {"unite_legale": {
    "etablissement_siege": {},
    "etablissements": []
}}
DEFAULT_DIGITAL_VENUE_LABEL = "Offre numérique"

class Post:
    class Returns201:
        @patch('connectors.api_entreprises.requests.get')
        @pytest.mark.usefixtures("db_session")
        def when_creating_a_virtual_venue(self, mock_api_entreprise, app):
            # given
            mock_api_entreprise.return_value = MagicMock(status_code=200,
                                                         text='',
                                                         json=MagicMock(return_value=copy.deepcopy(api_entreprise_json_mock)))

            user = create_user()
            digital_venue_type = create_venue_type(label=DEFAULT_DIGITAL_VENUE_LABEL)
            repository.save(user, digital_venue_type)
            body = {
                'name': 'Test Offerer',
                'siren': '418166096',
                'address': '123 rue de Paris',
                'postalCode': '93100',
                'city': 'Montreuil'
            }

            # when
            response = TestClient(app.test_client()) \
                .with_auth(user.email) \
                .post('/offerers', json=body)

            # then
            assert response.status_code == 201
            assert response.json['siren'] == '418166096'
            assert response.json['name'] == 'Test Offerer'
            virtual_venues = list(filter(lambda v: v['isVirtual'],
                                         response.json['managedVenues']))
            assert len(virtual_venues) == 1
            assert virtual_venues[0]["venueTypeId"] == humanize(digital_venue_type.id)


        @patch('connectors.api_entreprises.requests.get')
        @pytest.mark.usefixtures("db_session")
        def when_no_address_is_provided(self, mock_api_entreprise, app):
            # given
            mock_api_entreprise.return_value = MagicMock(status_code=200,
                                                         text='',
                                                         json=MagicMock(return_value=copy.deepcopy(api_entreprise_json_mock)))

            user = create_user()
            digital_venue_type = create_venue_type(label=DEFAULT_DIGITAL_VENUE_LABEL)
            repository.save(user, digital_venue_type)
            body = {
                'name': 'Test Offerer',
                'siren': '418166096',
                'postalCode': '93100',
                'city': 'Montreuil'
            }

            # when
            response = TestClient(app.test_client()) \
                .with_auth(user.email) \
                .post('/offerers', json=body)

            # then
            assert response.status_code == 201
            assert response.json['siren'] == '418166096'
            assert response.json['name'] == 'Test Offerer'

        @patch('connectors.api_entreprises.requests.get')
        @pytest.mark.usefixtures("db_session")
        def when_current_user_is_admin(self, mock_api_entreprise, app):
            # Given
            mock_api_entreprise.return_value = MagicMock(status_code=200,
                                                         text='',
                                                         json=MagicMock(return_value=copy.deepcopy(api_entreprise_json_mock)))

            user = create_user(can_book_free_offers=False, is_admin=True)
            digital_venue_type = create_venue_type(label=DEFAULT_DIGITAL_VENUE_LABEL)
            repository.save(user, digital_venue_type)
            body = {
                'name': 'Test Offerer',
                'siren': '418166096',
                'address': '123 rue de Paris',
                'postalCode': '93100',
                'city': 'Montreuil'
            }

            # When
            response = TestClient(app.test_client()) \
                .with_auth(user.email) \
                .post('/offerers', json=body)

            # then
            assert response.status_code == 201

        @patch('connectors.api_entreprises.requests.get')
        @pytest.mark.usefixtures("db_session")
        def expect_the_current_user_to_be_editor_of_the_new_offerer(self, mock_api_entreprise, app):
            # Given
            mock_api_entreprise.return_value = MagicMock(status_code=200,
                                                         text='',
                                                         json=MagicMock(return_value=copy.deepcopy(api_entreprise_json_mock)))

            user = create_user(can_book_free_offers=False, is_admin=False)
            digital_venue_type = create_venue_type(label=DEFAULT_DIGITAL_VENUE_LABEL)
            repository.save(user, digital_venue_type)
            body = {
                'name': 'Test Offerer',
                'siren': '418166096',
                'address': '123 rue de Paris',
                'postalCode': '93100',
                'city': 'Montreuil'
            }

            # when
            response = TestClient(app.test_client()) \
                .with_auth(user.email) \
                .post('/offerers', json=body)

            # then
            assert response.status_code == 201
            offerer = Offerer.query.first()
            assert offerer.UserOfferers[0].rights == RightsType.editor

        @patch('domain.admin_emails.make_validation_email_object')
        @patch('connectors.api_entreprises.requests.get')
        @pytest.mark.usefixtures("db_session")
        def when_offerer_already_have_user_offerer_new_user_offerer_has_validation_token(self,
                                                                                         mock_api_entreprise,
                                                                                         make_validation_email_object,
                                                                                         app):
            # Given
            make_validation_email_object.return_value={'Html-part': None}
            mock_api_entreprise.return_value = MagicMock(status_code=200,
                                                         text='',
                                                         json=MagicMock(return_value=copy.deepcopy(api_entreprise_json_mock)))

            user = create_user(can_book_free_offers=False, is_admin=False)
            user_2 = create_user(email="other_offerer@mail.com", is_admin=False)
            offerer = create_offerer()
            user_offerer = create_user_offerer(user_2, offerer, validation_token=None)
            digital_venue_type = create_venue_type(label=DEFAULT_DIGITAL_VENUE_LABEL)
            repository.save(user, user_2, offerer, user_offerer, digital_venue_type)
            body = {
                'name': 'Test Offerer',
                'siren': '123456789',
                'address': '123 rue de Paris',
                'postalCode': '93100',
                'city': 'Montreuil'
            }

            # when
            response = TestClient(app.test_client()) \
                .with_auth(user.email) \
                .post('/offerers', json=body)

            # then
            assert response.status_code == 201
            offerer = Offerer.query.first()
            created_user_offerer = UserOfferer.query \
                .filter(UserOfferer.offerer == offerer) \
                .filter(UserOfferer.user == user) \
                .one()
            assert created_user_offerer.validationToken is not None

        @patch('domain.admin_emails.make_validation_email_object')
        @patch('connectors.api_entreprises.requests.get')
        @pytest.mark.usefixtures("db_session")
        def expect_new_offerer_to_have_validation_token_but_user_offerer_dont(self,
                                                                              mock_api_entreprise,
                                                                              make_validation_email_object,
                                                                              app):
            # Given
            make_validation_email_object.return_value={'Html-part': None}
            mock_api_entreprise.return_value = MagicMock(status_code=200,
                                                         text='',
                                                         json=MagicMock(return_value=copy.deepcopy(api_entreprise_json_mock)))

            user = create_user(can_book_free_offers=False, is_admin=False)
            digital_venue_type = create_venue_type(label=DEFAULT_DIGITAL_VENUE_LABEL)
            repository.save(user, digital_venue_type)
            body = {
                'name': 'Test Offerer',
                'siren': '418166096',
                'address': '123 rue de Paris',
                'postalCode': '93100',
                'city': 'Montreuil'
            }

            # when
            response = TestClient(app.test_client()) \
                .with_auth(user.email) \
                .post('/offerers', json=body)

            # then
            assert response.status_code == 201
            offerer = Offerer.query.first()
            assert offerer.validationToken is not None
            assert offerer.UserOfferers[0].validationToken is None

        @patch('domain.admin_emails.make_validation_email_object')
        @patch('connectors.api_entreprises.requests.get')
        @pytest.mark.usefixtures("db_session")
        def when_offerer_already_in_base_just_create_user_offerer_with_validation_token(self,
                                                                                        mock_api_entreprise,
                                                                                        make_validation_email_object,
                                                                                        app):
            # Given
            make_validation_email_object.return_value = {'Html-part': None}
            mock_api_entreprise.return_value = MagicMock(status_code=200,
                                                         text='',
                                                         json=MagicMock(return_value=copy.deepcopy(api_entreprise_json_mock)))

            user = create_user(can_book_free_offers=False, is_admin=False)
            offerer = create_offerer(siren='123456789')
            repository.save(user, offerer)
            body = {
                'name': 'Test Offerer',
                'siren': '123456789',
                'address': '123 rue de Paris',
                'postalCode': '93100',
                'city': 'Montreuil'
            }

            # When
            response = TestClient(app.test_client()) \
                .with_auth(user.email) \
                .post('/offerers', json=body)

            # Then
            assert response.status_code == 201
            offerer = Offerer.query.first()
            assert offerer.UserOfferers[0].rights == RightsType.editor
            assert offerer.UserOfferers[0].validationToken is not None

        @patch('domain.admin_emails.make_validation_email_object')
        @patch('connectors.api_entreprises.requests.get')
        @pytest.mark.usefixtures("db_session")
        def expect_not_validated_offerer_to_keeps_validation_token_and_user_offerer_get_one(self,
                                                                                            mock_api_entreprise,
                                                                                            make_validation_email_object,
                                                                                            app):
            # Given
            make_validation_email_object.return_value = {'Html-part': None}
            mock_api_entreprise.return_value = MagicMock(status_code=200,
                                                         text='',
                                                         json=MagicMock(return_value=copy.deepcopy(api_entreprise_json_mock)))

            user = create_user(can_book_free_offers=False, is_admin=False)
            offerer = create_offerer(siren='123456789', validation_token='not_validated')
            repository.save(user, offerer)
            body = {
                'name': 'Test Offerer',
                'siren': '123456789',
                'address': '123 rue de Paris',
                'postalCode': '93100',
                'city': 'Montreuil'
            }

            # When
            response = TestClient(app.test_client()) \
                .with_auth(user.email) \
                .post('/offerers', json=body)

            # Then
            assert response.status_code == 201
            offerer = Offerer.query.first()
            assert offerer.validationToken == 'not_validated'
            assert offerer.UserOfferers[0].validationToken is not None
            user_offerer = UserOfferer.query.first()
            make_validation_email_object.assert_called_once_with(offerer, user_offerer)

        @patch('routes.offerers.maybe_send_offerer_validation_email', return_value=True)
        @patch('connectors.api_entreprises.requests.get')
        @patch('routes.offerers.send_raw_email', return_value=True)
        @pytest.mark.usefixtures("db_session")
        def expect_maybe_send_offerer_validation_email_to_be_called(self,
                                                                    mock_send_raw_email,
                                                                    mock_api_entreprise,
                                                                    mock_maybe_send_offerer_validation_email,
                                                                    app):
            # Given
            mock_api_entreprise.return_value = MagicMock(status_code=200,
                                                         text='',
                                                         json=MagicMock(return_value=copy.deepcopy(api_entreprise_json_mock)))

            user = create_user(can_book_free_offers=False, is_admin=False)
            offerer = create_offerer(siren='123456789', validation_token='not_validated')
            repository.save(user, offerer)
            body = {
                'name': 'Test Offerer',
                'siren': '123456789',
                'address': '123 rue de Paris',
                'postalCode': '93100',
                'city': 'Montreuil'
            }

            # When
            response = TestClient(app.test_client()) \
                .with_auth(user.email) \
                .post('/offerers', json=body)

            # Then
            assert response.status_code == 201
            offerer = Offerer.query.first()
            assert offerer.validationToken == 'not_validated'
            assert offerer.UserOfferers[0].validationToken is not None

            user_offerer = UserOfferer.query.first()

            mock_maybe_send_offerer_validation_email.assert_called_once_with(offerer, user_offerer, mock_send_raw_email)

        @patch('routes.offerers.send_ongoing_offerer_attachment_information_email_to_pro', return_value=True)
        @patch('connectors.api_entreprises.requests.get')
        @patch('routes.offerers.send_raw_email', return_value=True)
        @pytest.mark.usefixtures("db_session")
        def expect_send_ongoing_offerer_attachment_information_email_to_pro_to_be_called(self,
                                                                                         mock_send_raw_email,
                                                                                         mock_api_entreprise,
                                                                                         mock_send_ongoing_offerer_attachment_information_email_to_pro,
                                                                                         app):
            # Given
            mock_api_entreprise.return_value = MagicMock(status_code=200,
                                                         text='',
                                                         json=MagicMock(return_value=copy.deepcopy(api_entreprise_json_mock)))

            user = create_user(can_book_free_offers=False, is_admin=False)
            offerer = create_offerer(siren='123456789', validation_token='not_validated')
            repository.save(user, offerer)
            body = {
                'name': 'Test Offerer',
                'siren': '123456789',
                'address': '123 rue de Paris',
                'postalCode': '93100',
                'city': 'Montreuil'
            }

            # When
            response = TestClient(app.test_client()) \
                .with_auth(user.email) \
                .post('/offerers', json=body)

            # Then
            assert response.status_code == 201
            user_offerer = UserOfferer.query.first()

            mock_send_ongoing_offerer_attachment_information_email_to_pro.assert_called_once_with(user_offerer,
                                                                                                  mock_send_raw_email)

    @patch('routes.offerers.send_pro_user_waiting_for_validation_by_admin_email', return_value=True)
    @patch('connectors.api_entreprises.requests.get')
    @patch('routes.offerers.send_raw_email', return_value=True)
    @pytest.mark.usefixtures("db_session")
    def expect_send_pro_user_waiting_for_validation_by_admin_email_to_be_called_when_offerer_not_existing_yet(self,
                                                                mock_send_raw_email,
                                                                mock_api_entreprise,
                                                                mock_send_pro_user_waiting_for_validation_by_admin_email,
                                                                app):
        # Given
        mock_api_entreprise.return_value = MagicMock(status_code=200,
                                                     text='',
                                                     json=MagicMock(return_value=copy.deepcopy(api_entreprise_json_mock)))

        user = create_user(can_book_free_offers=False, is_admin=False)
        digital_venue_type = create_venue_type(label=DEFAULT_DIGITAL_VENUE_LABEL)
        repository.save(user, digital_venue_type)
        body = {
            'name': 'Test Offerer',
            'siren': '123456789',
            'address': '123 rue de Paris',
            'postalCode': '93100',
            'city': 'Montreuil'
        }

        # When
        response = TestClient(app.test_client()) \
            .with_auth(user.email) \
            .post('/offerers', json=body)

        # Then
        assert response.status_code == 201
        offerer = Offerer.query.first()

        mock_send_pro_user_waiting_for_validation_by_admin_email.assert_called_once_with(user, mock_send_raw_email, offerer)
