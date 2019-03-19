from datetime import datetime

import pytest

from models import PcObject
from models.db import db
from models.pc_object import serialize
from tests.conftest import clean_database, TestClient
from tests.test_utils import create_user, create_offerer, create_user_offerer, create_venue, \
    create_thing_offer, API_URL, create_event, create_event_offer, create_thing
from utils.human_ids import humanize


@pytest.mark.standalone
class Patch:
    class Returns200:
        @clean_database
        def when_updating_offer_booking_email(self, app):
            # Given
            user = create_user()
            offerer = create_offerer()
            user_offerer = create_user_offerer(user, offerer)
            venue = create_venue(offerer)
            offer = create_thing_offer(venue, booking_email='old@email.com')

            PcObject.check_and_save(offer, user, user_offerer)

            json = {
                'bookingEmail': 'offer@email.com',
            }

            # When
            response = TestClient().with_auth(user.email).patch(
                f'{API_URL}/offer/{humanize(offer.id)}',
                json=json)

            # Then
            assert response.status_code == 200
            db.session.refresh(offer)
            assert offer.bookingEmail == 'offer@email.com'

        @clean_database
        def when_user_updating_thing_offer_is_linked_to_same_owning_offerer(self, app):
            # Given
            user = create_user(email='editor@email.com')
            owning_offerer = create_offerer()
            user_offerer = create_user_offerer(user, owning_offerer)
            venue = create_venue(owning_offerer)
            thing = create_thing(thing_name='Old Name', owning_offerer=owning_offerer)
            offer = create_thing_offer(venue, thing)

            PcObject.check_and_save(offer, user_offerer)

            json = {
                'thing':
                    {
                        'name': 'New Name'
                    }
            }

            # When
            response = TestClient().with_auth(user.email).patch(
                f'{API_URL}/offer/{humanize(offer.id)}',
                json=json)

            # Then
            assert response.status_code == 200
            db.session.refresh(offer)
            db.session.refresh(thing)
            assert offer.name == 'New Name'
            assert thing.name == 'New Name'

        @clean_database
        def when_user_updating_thing_offer_is_not_linked_to_owningOfferers_offerers(self, app):
            # Given
            user = create_user(email='editor@email.com')
            owning_offerer = create_offerer(siren='123456789')
            editor_offerer = create_offerer(siren='123456780')
            editor_user_offerer = create_user_offerer(user, editor_offerer)
            venue = create_venue(editor_offerer)
            thing = create_thing(thing_name='Old Name', owning_offerer=owning_offerer)
            offer = create_thing_offer(venue, thing)

            PcObject.check_and_save(offer, editor_user_offerer, owning_offerer)

            json = {
                'thing':
                    {
                        'name': 'New Name'
                    }
            }

            # When
            response = TestClient().with_auth(user.email).patch(
                f'{API_URL}/offer/{humanize(offer.id)}',
                json=json)

            # Then
            assert response.status_code == 200
            db.session.refresh(offer)
            db.session.refresh(thing)
            assert offer.name == 'New Name'
            assert thing.name == 'Old Name'

        @clean_database
        def when_user_updating_thing_offer_has_rights_on_offer_but_no_owningOfferer_for_thing(self, app):
            # Given
            user = create_user(email='editor@email.com')
            offerer = create_offerer(siren='123456780')
            user_offerer = create_user_offerer(user, offerer)
            venue = create_venue(offerer)
            thing = create_thing(thing_name='Old Name', owning_offerer=None)
            offer = create_thing_offer(venue, thing)

            PcObject.check_and_save(offer, user_offerer)

            json = {
                'thing':
                    {
                        'name': 'New Name'
                    }
            }

            # When
            response = TestClient().with_auth(user.email).patch(
                f'{API_URL}/offer/{humanize(offer.id)}',
                json=json)

            # Then
            assert response.status_code == 200
            db.session.refresh(offer)
            db.session.refresh(thing)
            assert offer.name == 'New Name'
            assert thing.name == 'Old Name'

    class Returns400:
        @clean_database
        def when_trying_to_patch_forbidden_keys(self, app):
            # Given
            user = create_user()
            offerer = create_offerer()
            user_offerer = create_user_offerer(user, offerer)
            venue = create_venue(offerer)
            thing = create_thing(thing_name='Old Name', owning_offerer=None)
            offer = create_thing_offer(venue, thing)

            PcObject.check_and_save(offer, user, user_offerer)

            forbidden_keys = ['idAtProviders', 'dateModifiedAtLastProvider', 'thumbCount', 'firstThumbDominantColor',
                              'owningOffererId', 'id', 'lastProviderId', 'isNational', 'dateCreated']

            json = {
                'id': 1,
                'dateCreated': serialize(datetime(2019, 1, 1)),
                'isNational': True,
                'lastProviderId': 1,
                'thing':
                    {
                        'owningOffererId': 'AA',
                        'idAtProviders': 1,
                        'dateModifiedAtLastProvider': serialize(datetime(2019, 1, 1)),
                        'thumbCount': 2,
                        'firstThumbDominantColor': ''
                    }
            }

            # When
            response = TestClient().with_auth(user.email).patch(
                f'{API_URL}/offer/{humanize(offer.id)}',
                json=json)

            # Then
            assert response.status_code == 400
            assert response.json()['owningOffererId'] == ['Vous ne pouvez pas modifier cette information']
            for key in forbidden_keys:
                assert key in response.json()

    class Returns403:
        @clean_database
        def when_user_is_not_attached_to_offerer(self, app):
            # Given
            user = create_user()
            offerer = create_offerer()
            event = create_event(event_name='Old name')
            venue = create_venue(offerer)
            offer = create_event_offer(venue, event)

            PcObject.check_and_save(event, offer, user, venue)

            json = {
                'name': 'New name',
                'venueId': humanize(venue.id)
            }

            # When
            response = TestClient().with_auth(user.email).patch(
                f'{API_URL}/offer/{humanize(offer.id)}',
                json=json)

            # Then
            assert response.status_code == 403
            assert response.json()['global'] == ["Cette structure n'est pas enregistrée chez cet utilisateur."]


@pytest.mark.standalone
class Patch:
    class Returns200:
        @clean_database
        def test_returns_200_and_expires_recos(self, app):
            # given
            user = create_user()
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_event_offer(venue)
            user_offerer = create_user_offerer(user, offerer)
            recommendation = create_recommendation(offer, user, valid_until_date=datetime.utcnow() + timedelta(days=7))
            PcObject.check_and_save(offer, user, venue, offerer, recommendation, user_offerer)

            auth_request = TestClient().with_auth(email=user.email)
            data = {'eventId': 'AE', 'isActive': False}

            # when
            response = auth_request.patch(API_URL + '/offers/%s' % humanize(offer.id), json=data)

            # then
            db.session.refresh(offer)
            assert response.status_code == 200
            assert response.json()['id'] == humanize(offer.id)
            assert response.json()['isActive'] == offer.isActive
            assert offer.isActive == data['isActive']
            # only isActive can be modified
            assert offer.eventId != data['eventId']
            assert response.json()['eventId'] != offer.eventId
            db.session.refresh(recommendation)
            assert recommendation.validUntilDate < datetime.utcnow()

    class Returns403:
        @clean_database
        def test_returns_403_if_user_is_not_attached_to_offerer_of_offer(self, app):
            # given
            current_user = create_user(email='bobby@test.com')
            other_user = create_user(email='jimmy@test.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_event_offer(venue)
            user_offerer = create_user_offerer(other_user, offerer)
            PcObject.check_and_save(offer, other_user, current_user, venue, offerer, user_offerer)

            auth_request = TestClient().with_auth(email=current_user.email)

            # when
            response = auth_request.patch(API_URL + '/offers/%s' % humanize(offer.id), json={})

            # then
            error_message = response.json()
            assert response.status_code == 403
            assert error_message['global'] == ['Cette structure n\'est pas enregistrée chez cet utilisateur.']

    class Returns404:
        @clean_database
        def test_returns_404_if_offer_does_not_exist(self, app):
            # given
            user = create_user()
            PcObject.check_and_save(user)
            auth_request = TestClient().with_auth(email=user.email)

            # when
            response = auth_request.patch(API_URL + '/offers/ADFGA', json={})

            # then
            assert response.status_code == 404
