from unittest.mock import patch

from models import Venue
from repository import repository
from tests.conftest import clean_database, TestClient
from tests.model_creators.generic_creators import create_user, create_offerer, create_venue, create_user_offerer
from tests.model_creators.specific_creators import create_offer_with_thing_product
from utils.human_ids import humanize


class Patch:
    class Returns200:
        @clean_database
        def when_there_is_no_siret_yet(self, app):
            # Given
            offerer = create_offerer()
            user = create_user()
            user_offerer = create_user_offerer(user, offerer, is_admin=True)
            siret = offerer.siren + '11111'
            venue = create_venue(offerer, comment="Pas de siret", siret=None)
            repository.save(user_offerer, venue)
            venue_data = {
                'siret': siret,
            }

            auth_request = TestClient(app.test_client()).with_auth(email=user.email)

            # when
            response = auth_request.patch('/venues/%s' % humanize(venue.id), json=venue_data)

            # Then
            assert response.status_code == 200
            assert response.json['siret'] == siret

        @clean_database
        @patch('routes.venues.redis.add_venue_id_to_list')
        def when_updating_a_venue_on_public_name_expect_relative_venue_id_to_be_added_to_redis(self, mock_add_venue_id_to_redis, app):
            # Given
            offerer = create_offerer()
            user = create_user()
            user_offerer = create_user_offerer(user, offerer, is_admin=True)
            venue = create_venue(offerer, public_name="My old name")
            repository.save(user_offerer, venue)
            venue_data = {
                'publicName': 'Mon nouveau nom',
            }

            auth_request = TestClient(app.test_client()).with_auth(email=user.email)

            # when
            response = auth_request.patch('/venues/%s' % humanize(venue.id), json=venue_data)

            # Then
            assert response.status_code == 200
            mock_add_venue_id_to_redis.assert_called_once_with(client=app.redis_client, venue_id=venue.id)

        @clean_database
        @patch('routes.venues.redis.add_venue_id_to_list')
        def when_updating_a_venue_on_siret_expect_relative_venue_id_to_not_be_added_to_redis(self, mock_add_venue_id_to_redis, app):
            # Given
            offerer = create_offerer()
            user = create_user()
            user_offerer = create_user_offerer(user, offerer, is_admin=True)
            siret = offerer.siren + '11111'
            venue = create_venue(offerer, comment="Pas de siret", siret=None)
            repository.save(user_offerer, venue)
            venue_data = {
                'siret': siret,
            }

            auth_request = TestClient(app.test_client()).with_auth(email=user.email)

            # when
            response = auth_request.patch('/venues/%s' % humanize(venue.id), json=venue_data)

            # Then
            assert response.status_code == 200
            mock_add_venue_id_to_redis.assert_not_called()

        @clean_database
        def when_there_is_already_one_equal_siret(self, app):
            # Given
            offerer = create_offerer()
            user = create_user()
            user_offerer = create_user_offerer(user, offerer, is_admin=True)
            siret = offerer.siren + '11111'
            venue = create_venue(offerer, siret=siret)
            repository.save(user_offerer, venue)
            venue_data = {
                'siret': siret,
            }
            auth_request = TestClient(app.test_client()).with_auth(email=user.email)

            # when
            response = auth_request.patch('/venues/%s' % humanize(venue.id), json=venue_data)

            # Then
            assert response.status_code == 200
            assert response.json['siret'] == siret

        @clean_database
        def when_user_has_rights_on_managing_offerer(self, app):
            # given
            offerer = create_offerer()
            user = create_user(email='user.pro@test.com')
            venue = create_venue(offerer, name='L\'encre et la plume')
            user_offerer = create_user_offerer(user, offerer)
            repository.save(user_offerer, venue)
            auth_request = TestClient(app.test_client()).with_auth(email=user.email)
            venue_id = venue.id

            # when
            response = auth_request.patch('/venues/%s' % humanize(venue.id), json={'name': 'Ma librairie'})

            # then
            assert response.status_code == 200
            venue = Venue.query.get(venue_id)
            assert venue.name == 'Ma librairie'
            json = response.json
            assert json['isValidated'] == True
            assert 'validationToken' not in json
            assert venue.isValidated

    class Returns400:
        @clean_database
        def when_trying_to_patch_siret_when_already_one(self, app):
            # Given
            offerer = create_offerer()
            user = create_user()
            user_offerer = create_user_offerer(user, offerer, is_admin=True)
            siret = offerer.siren + '11111'
            venue = create_venue(offerer, siret=siret)
            repository.save(user_offerer, venue)
            venue_data = {
                'siret': offerer.siren + '12345',
            }
            auth_request = TestClient(app.test_client()).with_auth(email=user.email)

            # when
            response = auth_request.patch('/venues/%s' % humanize(venue.id), json=venue_data)

            # Then
            assert response.status_code == 400
            assert response.json['siret'] == ['Vous ne pouvez pas modifier le siret d\'un lieu']

        @clean_database
        def when_editing_is_virtual_and_managing_offerer_already_has_virtual_venue(self, app):
            # given
            offerer = create_offerer()
            user = create_user(email='user.pro@test.com')
            venue1 = create_venue(offerer, name='Les petits papiers', is_virtual=True, siret=None)
            venue2 = create_venue(offerer, name='L\'encre et la plume', is_virtual=False)
            user_offerer = create_user_offerer(user, offerer)
            repository.save(user_offerer, venue1, venue2)
            auth_request = TestClient(app.test_client()).with_auth(email=user.email)

            # when
            response = auth_request.patch('/venues/%s' % humanize(venue2.id), json={'isVirtual': True})

            # then
            assert response.status_code == 400
            assert response.json == {
                'isVirtual': ['Un lieu pour les offres numériques existe déjà pour cette structure']}

        @clean_database
        def when_latitude_out_of_range_and_longitude_wrong_format(self, app):
            # given
            offerer = create_offerer()
            user = create_user(email='user.pro@test.com')
            venue = create_venue(offerer, name='Les petits papiers', is_virtual=False)
            user_offerer = create_user_offerer(user, offerer)
            repository.save(user_offerer, venue)
            auth_request = TestClient(app.test_client()).with_auth(email=user.email)
            data = {'latitude': -98.82387, 'longitude': '112°3534'}

            # when
            response = auth_request.patch('/venues/%s' % humanize(venue.id), json=data)

            # then
            assert response.status_code == 400
            assert response.json['latitude'] == ['La latitude doit être comprise entre -90.0 et +90.0']
            assert response.json['longitude'] == ['Format incorrect']

        @clean_database
        def when_trying_to_edit_managing_offerer(self, app):
            # Given
            offerer = create_offerer(siren='123456789')
            other_offerer = create_offerer(siren='987654321')
            user = create_user(email='user.pro@test.com')
            venue = create_venue(offerer, name='Les petits papiers', is_virtual=False)
            user_offerer = create_user_offerer(user, offerer)
            repository.save(user_offerer, venue, other_offerer)
            auth_request = TestClient(app.test_client()).with_auth(email=user.email)

            # When
            response = auth_request.patch('/venues/%s' % humanize(venue.id),
                                          json={'managingOffererId': humanize(other_offerer.id)})

            # Then
            assert response.status_code == 400
            assert response.json['managingOffererId'] == ['Vous ne pouvez pas changer la structure d\'un lieu']
