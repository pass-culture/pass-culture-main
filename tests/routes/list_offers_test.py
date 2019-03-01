""" routes offers tests """
import pytest
import secrets
from datetime import datetime, timedelta

from models import PcObject, Venue, EventType, ThingType
from tests.conftest import clean_database, TestClient
from tests.test_utils import API_URL, \
    create_event, \
    create_event_offer, \
    create_offerer, \
    create_thing, \
    create_thing_offer, \
    create_user, \
    create_user_offerer, \
    create_venue, \
    create_stock_from_offer
from utils.human_ids import dehumanize, humanize


@pytest.mark.standalone
class Get:
    class Returns200:
        @clean_database
        def test_results_are_paginated_by_chunks_of_10(self, app):
            # Given
            user = create_user(email='user@test.com', password='azerty123')
            create_offers_for(user, 20)

            # when
            response = TestClient().with_auth(email='user@test.com', password='azerty123').get(API_URL + '/offers')

            # then
            offers = response.json()
            assert response.status_code == 200
            assert len(offers) == 10

        @clean_database
        def test_results_are_paginated_by_default_on_page_1(self, app):
            # given
            user = create_user(email='user@test.com', password='azerty123')
            create_offers_for(user, 20)
            auth_request = TestClient().with_auth(email='user@test.com', password='azerty123')
            offers = auth_request.get(API_URL + '/offers').json()
            first_id = dehumanize(offers[0]['id'])

            # when
            response = auth_request.get(API_URL + '/offers?page=1')

            # then
            result = response.json()
            assert response.status_code == 200
            assert dehumanize(result[0]['id']) == first_id

        @clean_database
        def test_returns_offers_sorted_by_id_desc(self, app):
            # given
            user = create_user(email='user@test.com', password='azerty123')
            create_offers_for(user, 20)
            auth_request = TestClient().with_auth(email='user@test.com', password='azerty123')
            response_1 = auth_request.get(API_URL + '/offers?page=1')

            # when
            response_2 = auth_request.get(API_URL + '/offers?page=2')

            # then
            offers_1 = response_1.json()
            offers_2 = response_2.json()
            assert offers_1[-1]['dateCreated'] > offers_2[0]['dateCreated']

        @clean_database
        def test_results_are_filtered_by_given_venue_id(self, app):
            # given
            user = create_user(email='user@test.com', password='azerty123')
            create_offers_for(user, 20, siren='123456789')
            create_offers_for(user, 20, siren='987654321')
            auth_request = TestClient().with_auth(email='user@test.com', password='azerty123')
            venue_id = Venue.query.first().id

            # when
            response = auth_request.get(API_URL + '/offers?venueId=' + humanize(venue_id))

            # then
            offers = response.json()
            assert response.status_code == 200
            for offer in offers:
                assert offer['venueId'] == humanize(venue_id)

        @clean_database
        def test_can_be_filtered_and_paginated_at_the_same_time(self, app):
            # given
            user = create_user(email='user@test.com', password='azerty123')
            create_offers_for(user, 20, siren='987654321')
            auth_request = TestClient().with_auth(email='user@test.com', password='azerty123')
            venue_id = Venue.query.first().id

            # when
            response = auth_request.get(API_URL + '/offers?venueId=' + humanize(venue_id) + '&page=2')

            # then
            offers = response.json()
            assert response.status_code == 200
            for offer in offers:
                assert offer['venueId'] == humanize(venue_id)

        @clean_database
        def test_can_be_searched_and_filtered_and_paginated_at_the_same_time(self, app):
            # given
            user = create_user(email='user@test.com', password='azerty123')
            create_offers_for(user, 20, siren='987654321')
            auth_request = TestClient().with_auth(email='user@test.com', password='azerty123')
            venue_id = Venue.query.first().id

            # when
            response = auth_request.get(API_URL + '/offers?venueId=' + humanize(venue_id) + '&page=1&keywords=Event')

            # then
            offers = response.json()
            assert response.status_code == 200
            assert len(offers) == 10
            for offer in offers:
                assert offer['venueId'] == humanize(venue_id)
                assert 'event' in offer['event']['name'].lower()

        @clean_database
        def test_can_be_searched_using_multiple_search_terms(self, app):
            # given
            user = create_user(email='user@test.com', password='azerty123')
            create_offers_for(user, 20, siren='987654321')
            auth_request = TestClient().with_auth(email='user@test.com', password='azerty123')
            venue_id = Venue.query.first().id

            # when
            response = auth_request.get(
                API_URL + '/offers?venueId=' + humanize(venue_id) + '&page=1&search=Event Offer')

            # then
            offers = response.json()
            assert response.status_code == 200
            assert len(offers) == 10
            assert len([o for o in offers if 'event' in o]) > 0
            assert len([o for o in offers if 'thing' in o]) > 0

        @clean_database
        def test_list_activation_offers_returns_offers_of_event_type(self, app):
            # given
            user = create_user(password='p@55sw0rd')
            PcObject.check_and_save(user)
            auth_request = TestClient().with_auth(email=user.email, password='p@55sw0rd')
            now = datetime.utcnow()
            five_days_ago = now - timedelta(days=5)
            next_week = now + timedelta(days=7)
            offerer = create_offerer()
            venue1 = create_venue(offerer, siret=offerer.siren + '12345', postal_code='93000', departement_code='93')
            venue2 = create_venue(offerer, siret=offerer.siren + '67890', postal_code='93000', departement_code='93')
            venue3 = create_venue(offerer, siret=offerer.siren + '54321', postal_code='93000', departement_code='93')
            offer1 = create_event_offer(venue1, event_type=EventType.ACTIVATION)
            offer2 = create_event_offer(venue2, event_type=EventType.ACTIVATION)
            offer3 = create_event_offer(venue3, event_type=EventType.ACTIVATION)
            stock1 = create_stock_from_offer(offer1, price=0, booking_limit_datetime=five_days_ago)
            stock2 = create_stock_from_offer(offer2, price=0, booking_limit_datetime=next_week)
            stock3 = create_stock_from_offer(offer3, price=0, booking_limit_datetime=None)
            PcObject.check_and_save(stock1, stock2, stock3)

            # when
            response = auth_request.get(API_URL + '/offers/activation')

            # then
            json = response.json()
            event_ids = list(map(lambda x: x['eventId'], json))
            assert len(json) == 2
            assert response.status_code == 200
            assert humanize(offer2.eventId) in event_ids
            assert humanize(offer3.eventId) in event_ids

        @clean_database
        def test_returns_list_of_offers_with_thing_or_event_with_type_details(self, app):
            # given
            user = create_user(password='p@55sw0rd', is_admin=True, can_book_free_offers=False)
            offerer = create_offerer()
            venue = create_venue(offerer, siret=offerer.siren + '12345', postal_code='93000', departement_code='93')
            event_offer = create_event_offer(venue, event_type=EventType.SPECTACLE_VIVANT)
            thing_offer = create_thing_offer(venue, thing_type=ThingType.LIVRE_EDITION)
            stock_event = create_stock_from_offer(event_offer, price=0)
            stock_thing = create_stock_from_offer(thing_offer, price=0)
            PcObject.check_and_save(user, stock_event, stock_thing)

            expected_thing_type = {
                'label': "Livre — Édition",
                'offlineOnly': False,
                'onlineOnly': False,
                'sublabel': "Lire",
                'description': "S’abonner à un quotidien d’actualité ? À un hebdomadaire humoristique ? À un mensuel dédié à la nature ? Acheter une BD ou un manga ? Ou tout simplement ce livre dont tout le monde parle ?",
                'type': 'Thing',
                'value': 'ThingType.LIVRE_EDITION'
            }
            expected_event_type = {
                'label': "Spectacle vivant",
                'offlineOnly': True,
                'onlineOnly': False,
                'sublabel': "Applaudir",
                'description': "Suivre un géant de 12 mètres dans la ville ? Rire aux éclats devant un stand up ? Rêver le temps d’un opéra ou d’un spectacle de danse ? Assister à une pièce de théâtre, ou se laisser conter une histoire ?",
                'type': 'Event',
                'value': 'EventType.SPECTACLE_VIVANT'
            }

            auth_request = TestClient().with_auth(email=user.email, password='p@55sw0rd')

            # when
            response = auth_request.get(API_URL + '/offers')

            # then
            json = response.json()
            types = list(map(lambda x: x['thing']['offerType'] if 'thing' in x else x['event']['offerType'], json))
            thing_or_event_keys = list(map(lambda x: x['thing'].keys() if 'thing' in x else x['event'].keys(), json))
            assert response.status_code == 200
            assert expected_thing_type in types
            assert expected_event_type in types
            assert "type" not in thing_or_event_keys

        @clean_database
        def test_does_not_show_anything_to_user_offerer_when_not_validated(self, app):
            # Given
            user = create_user(password='azerty123')
            offerer = create_offerer()
            venue = create_venue(offerer)
            user_offerer = create_user_offerer(user, offerer, validation_token=secrets.token_urlsafe(20))
            offer = create_thing_offer(venue)
            PcObject.check_and_save(user_offerer, offer)
            auth_request = TestClient().with_auth(email=user.email, password='azerty123')
            # When
            response = auth_request.get(API_URL + '/offers')

            # Then
            assert response.status_code == 200
            assert response.json() == []


@pytest.mark.standalone
class Post:
    class Returns201:
        @clean_database
        def test_create_thing_offer(self, app):
            # given
            user = create_user(email='user@test.com', password='azerty123')
            offerer = create_offerer()
            user_offerer = create_user_offerer(user, offerer)
            venue = create_venue(offerer)
            thing = create_thing()
            PcObject.check_and_save(user_offerer, venue, thing)

            data = {
                'venueId': humanize(venue.id),
                'thingId': humanize(thing.id)
            }
            auth_request = TestClient().with_auth(email='user@test.com', password='azerty123')

            # when
            response = auth_request.post(API_URL + '/offers', json=data)

            # then
            assert response.status_code == 201

        @clean_database
        def test_create_event_offer(self, app):
            # given
            user = create_user(email='user@test.com', password='azerty123')
            offerer = create_offerer()
            user_offerer = create_user_offerer(user, offerer)
            venue = create_venue(offerer)
            event = create_event()
            PcObject.check_and_save(user_offerer, venue, event)

            data = {
                'venueId': humanize(venue.id),
                'eventId': humanize(event.id)
            }
            auth_request = TestClient().with_auth(email='user@test.com', password='azerty123')

            # when
            response = auth_request.post(API_URL + '/offers', json=data)

            # then
            assert response.status_code == 201

    class Returns400:
        @clean_database
        def test_create_thing_offer_returns_bad_request_if_thing_is_physical_and_venue_is_virtual(self, app):
            # given
            user = create_user(email='user@test.com', password='azerty123')
            offerer = create_offerer()
            user_offerer = create_user_offerer(user, offerer)
            venue = create_venue(offerer, is_virtual=True, siret=None)
            thing = create_thing(url=None)
            PcObject.check_and_save(user_offerer, venue, thing)

            data = {
                'venueId': humanize(venue.id),
                'thingId': humanize(thing.id)
            }
            auth_request = TestClient().with_auth(email='user@test.com', password='azerty123')

            # when
            response = auth_request.post(API_URL + '/offers', json=data)

            # then
            assert response.status_code == 400
            assert response.json() == {
                'global':
                    ['Offer.venue is virtual but Offer.thing does not have an URL']
            }

    class Returns403:
        @clean_database
        def when_user_is_not_attached_to_offerer(self, app):
            # given
            current_user = create_user(email='user@test.com', password='azerty123')
            other_user = create_user(email='jimmy@test.com', password='p@55sw0rd')
            offerer = create_offerer()

            other_user_offerer = create_user_offerer(other_user, offerer)

            venue = create_venue(offerer)
            event = create_event()
            PcObject.check_and_save(other_user, venue, event, current_user, other_user_offerer)

            data = {
                'venueId': humanize(venue.id),
                'eventId': humanize(event.id)
            }
            auth_request = TestClient().with_auth(email=current_user.email, password='azerty123')

            # when
            response = auth_request.post(API_URL + '/offers', json=data)

            # then
            error_message = response.json()
            assert response.status_code == 403
            assert error_message['global'] == ['Cette structure n\'est pas enregistrée chez cet utilisateur.']


def create_offers_for(user, n, siren='123456789'):
    offerer = create_offerer(siren=siren)
    user_offerer = create_user_offerer(user, offerer)
    venue = create_venue(offerer, siret=siren + '1345')
    offers = create_n_mixed_offers_with_same_venue(venue, n=n)

    PcObject.check_and_save(user_offerer)
    PcObject.check_and_save(*offers)


def create_n_mixed_offers_with_same_venue(venue, n=10):
    offers = []
    for i in range(n // 2, 0, -1):
        date_created = datetime.utcnow() - timedelta(days=i)
        offers.append(create_thing_offer(venue, date_created=date_created, thing_name='Thing Offer %s' % i))
        offers.append(create_event_offer(venue, event_name='Event Offer %s' % i, date_created=date_created))
    return offers
