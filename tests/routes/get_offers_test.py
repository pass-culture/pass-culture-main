import pytest
from datetime import datetime, timedelta
from pprint import pprint

from models import PcObject
from models.db import db
from tests.conftest import clean_database, TestClient
from tests.test_utils import API_URL, \
    create_booking, \
    create_deposit, \
    create_event_offer, \
    create_offerer, \
    create_recommendation, \
    create_user, \
    create_user_offerer, \
    create_stock_from_offer, \
    create_venue, create_thing_offer, create_bank_information
from utils.human_ids import humanize

@pytest.mark.standalone
class Get:
    class Returns200:
        @clean_database
        def when_a_thing_offer_but_there_is_no_stock_yet(self, app):
            # given
                user = create_user(email='user@test.com')
                offerer = create_offerer()
                user_offerer = create_user_offerer(user, offerer)
                venue = create_venue(offerer)
                offer = create_thing_offer(venue)

                PcObject.check_and_save(user, user_offerer, offer)

            # when
                response = TestClient().with_auth(email='user@test.com').get(API_URL + '/offers')

            # then
                response_json = response.json()
                pprint(response_json)
                assert response.status_code == 200
                assert 'stockAlertMessage' in response_json[0]
                assert response_json[0]['stockAlertMessage'] == "pas encore de stock"

        @clean_database
        def when_a_thing_offer_but_there_is_only_one_place_left(self, app):
            # given
                user = create_user(email='user@test.com')
                user2 = create_user(email='user2@test.com')
                offerer = create_offerer()
                user_offerer = create_user_offerer(user, offerer)
                venue = create_venue(offerer)
                offer = create_thing_offer(venue)

                recommendation = create_recommendation(offer, user)

                stock = create_stock_from_offer(offer, available=10)
                deposit = create_deposit(user2, datetime.utcnow(), amount=500)
                booking = create_booking(user2, stock, venue, recommendation, quantity=9)

                PcObject.check_and_save(booking, deposit, offer, recommendation, stock, user2, user_offerer)

            # when
                response = TestClient().with_auth(email='user@test.com').get(API_URL + f'/offers?')

            # then
                response_json = response.json()
                pprint(response_json)
                assert response.status_code == 200
                assert 'stockAlertMessage' in response_json[0]
                assert response_json[0]['stockAlertMessage'] == "encore 1 en stock"

        @clean_database
        def when_a_thing_offer_with_remaining_stock(self, app):
            # given
                user = create_user(email='user@test.com')
                user2 = create_user(email='user2@test.com')
                offerer = create_offerer()
                user_offerer = create_user_offerer(user, offerer)
                venue = create_venue(offerer)
                offer = create_thing_offer(venue)
                stock = create_stock_from_offer(offer, available=15)
                recommendation = create_recommendation(offer, user)

                deposit = create_deposit(user2, datetime.utcnow(), amount=500)
                booking = create_booking(user2, stock, venue, recommendation, quantity=3)

                PcObject.check_and_save(booking, deposit, user, offer, stock, user2, user_offerer)

            # when
                response = TestClient().with_auth(email='user@test.com').get(API_URL + f'/offers?')

            # then
                response_json = response.json()
                pprint(response_json)
                assert response.status_code == 200
                assert 'stockAlertMessage' in response_json[0]
                assert response_json[0]['stockAlertMessage'] == "encore 12 en stock"

        @clean_database
        def when_a_thing_offer_with_unlimited_and_remaining_stock(self, app):
            # given
                user = create_user(email='user@test.com')
                user2 = create_user(email='user2@test.com')
                offerer = create_offerer()
                user_offerer = create_user_offerer(user, offerer)
                venue = create_venue(offerer)
                offer = create_thing_offer(venue)
                stock = create_stock_from_offer(offer, available=15)
                stock2 = create_stock_from_offer(offer, available=None)
                recommendation = create_recommendation(offer, user)

                deposit = create_deposit(user2, datetime.utcnow(), amount=500)
                booking = create_booking(user2, stock, venue, recommendation, quantity=3)

                PcObject.check_and_save(booking, deposit, user, offer, stock, stock2, user2, user_offerer)

            # when
                response = TestClient().with_auth(email='user@test.com').get(API_URL + f'/offers?')

            # then
                response_json = response.json()
                pprint(response_json)
                assert response.status_code == 200
                assert 'stockAlertMessage' in response_json[0]

                assert response_json[0]['stockAlertMessage'] == 'encore 12 en stock'

        @clean_database
        def when_a_thing_offer_with_no_more_remaining_stock(self, app):
            # given
                user = create_user(email='user@test.com')
                user2 = create_user(email='user2@test.com')
                offerer = create_offerer()
                user_offerer = create_user_offerer(user, offerer)
                venue = create_venue(offerer)
                offer = create_thing_offer(venue)
                stock = create_stock_from_offer(offer, available=15)
                stock2 = create_stock_from_offer(offer, available=None)
                recommendation = create_recommendation(offer, user)

                deposit = create_deposit(user2, datetime.utcnow(), amount=500)
                booking = create_booking(user2, stock, venue, recommendation, quantity=15)

                PcObject.check_and_save(booking, deposit, user, offer, stock, stock2, user2, user_offerer)

            # when
                response = TestClient().with_auth(email='user@test.com').get(API_URL + f'/offers?')

            # then
                response_json = response.json()
                pprint(response_json)
                assert response.status_code == 200
                assert 'stockAlertMessage' in response_json[0]
                assert response_json[0]['stockAlertMessage'] == 'plus de stock pour 1 offre'

        @clean_database
        def when_a_thing_offer_with_only_unlimited_stocks(self, app):
            # given
                user = create_user(email='user@test.com')
                user2 = create_user(email='user2@test.com')
                offerer = create_offerer()
                user_offerer = create_user_offerer(user, offerer)
                venue = create_venue(offerer)
                offer = create_thing_offer(venue)
                stock = create_stock_from_offer(offer, available=None)
                stock2 = create_stock_from_offer(offer, available=None)
                recommendation = create_recommendation(offer, user)

                deposit = create_deposit(user2, datetime.utcnow(), amount=500)
                booking = create_booking(user2, stock, venue, recommendation, quantity=15)

                PcObject.check_and_save(booking, deposit, user, offer, stock, stock2, user2, user_offerer)

            # when
                response = TestClient().with_auth(email='user@test.com').get(API_URL + f'/offers?')

            # then
                response_json = response.json()
                pprint(response_json)
                assert response.status_code == 200
                assert 'stockAlertMessage' in response_json[0]
                assert response_json[0]['stockAlertMessage'] == 'illimité'

        @clean_database
        def when_an_event_offer_but_there_is_no_stock_yet(self, app):
            # given
                user = create_user(email='user@test.com')
                offerer = create_offerer()
                user_offerer = create_user_offerer(user, offerer)
                venue = create_venue(offerer)
                offer = create_event_offer(venue)

                PcObject.check_and_save(offer, user, user_offerer)

            # when
                response = TestClient().with_auth(email='user@test.com').get(API_URL + f'/offers?')

            # then
                response_json = response.json()
                pprint(response_json)
                assert response.status_code == 200
                assert 'stockAlertMessage' in response_json[0]
                assert response_json[0]['stockAlertMessage'] == "pas encore de places"

        @clean_database
        def when_an_event_offer_but_there_is_only_one_place_left(self, app):
            # given
                user = create_user(email='user@test.com')
                user2 = create_user(email='user2@test.com')
                offerer = create_offerer()
                user_offerer = create_user_offerer(user, offerer)
                venue = create_venue(offerer)
                offer = create_event_offer(venue)

                recommendation = create_recommendation(offer, user)

                stock = create_stock_from_offer(offer, available=10)
                deposit = create_deposit(user2, datetime.utcnow(), amount=500)
                booking = create_booking(user2, stock, venue, recommendation, quantity=9)

                PcObject.check_and_save(booking, deposit, offer, recommendation, stock, user2, user_offerer)

            # when
                response = TestClient().with_auth(email='user@test.com').get(API_URL + f'/offers?')

            # then
                response_json = response.json()
                pprint(response_json)
                assert response.status_code == 200
                assert 'stockAlertMessage' in response_json[0]
                assert response_json[0]['stockAlertMessage'] == "encore 1 place"

        @clean_database
        def when_an_event_offer_with_remaining_stock(self, app):
            # given
                user = create_user(email='user@test.com')
                user2 = create_user(email='user2@test.com')
                offerer = create_offerer()
                user_offerer = create_user_offerer(user, offerer)
                venue = create_venue(offerer)
                offer = create_event_offer(venue)
                stock = create_stock_from_offer(offer, available=15)
                recommendation = create_recommendation(offer, user)

                deposit = create_deposit(user2, datetime.utcnow(), amount=500)
                booking = create_booking(user2, stock, venue, recommendation, quantity=3)

                PcObject.check_and_save(booking, deposit, user, offer, stock, user2, user_offerer)

            # when
                response = TestClient().with_auth(email='user@test.com').get(API_URL + f'/offers?')

            # then
                response_json = response.json()
                pprint(response_json)
                assert response.status_code == 200
                assert 'stockAlertMessage' in response_json[0]
                assert response_json[0]['stockAlertMessage'] == "encore 12 places"

        @clean_database
        def when_an_event_offer_with_unlimited_and_remaining_stock(self, app):
            # given
                user = create_user(email='user@test.com')
                user2 = create_user(email='user2@test.com')
                offerer = create_offerer()
                user_offerer = create_user_offerer(user, offerer)
                venue = create_venue(offerer)
                offer = create_event_offer(venue)
                stock = create_stock_from_offer(offer, available=15)
                recommendation = create_recommendation(offer, user)

                deposit = create_deposit(user2, datetime.utcnow(), amount=500)
                booking = create_booking(user2, stock, venue, recommendation, quantity=3)

                PcObject.check_and_save(booking, deposit, user, offer, stock, user2, user_offerer)

            # when
                response = TestClient().with_auth(email='user@test.com').get(API_URL + f'/offers?')

            # then
                response_json = response.json()
                pprint(response_json)
                assert response.status_code == 200
                assert 'stockAlertMessage' in response_json[0]
                assert response_json[0]['stockAlertMessage'] == "encore 12 places"

        @clean_database
        def when_an_event_offer_with_no_more_remaining_stock(self, app):
            # given
                user = create_user(email='user@test.com')
                user2 = create_user(email='user2@test.com')
                offerer = create_offerer()
                user_offerer = create_user_offerer(user, offerer)
                venue = create_venue(offerer)
                offer = create_event_offer(venue)
                stock = create_stock_from_offer(offer, available=15)
                stock2 = create_stock_from_offer(offer, available=None)
                recommendation = create_recommendation(offer, user)

                deposit = create_deposit(user2, datetime.utcnow(), amount=500)
                booking = create_booking(user2, stock, venue, recommendation, quantity=15)

                PcObject.check_and_save(booking, deposit, user, offer, stock, stock2, user2, user_offerer)

            # when
                response = TestClient().with_auth(email='user@test.com').get(API_URL + f'/offers?')

            # then
                response_json = response.json()
                pprint(response_json)
                assert response.status_code == 200
                assert 'stockAlertMessage' in response_json[0]
                assert response_json[0]['stockAlertMessage'] == "plus de places pour 1 offre"

        @clean_database
        def when_an_event_offer_with_only_unlimited_stocks(self, app):
            # given
                user = create_user(email='user@test.com')
                user2 = create_user(email='user2@test.com')
                offerer = create_offerer()
                user_offerer = create_user_offerer(user, offerer)
                venue = create_venue(offerer)
                offer = create_event_offer(venue)
                stock = create_stock_from_offer(offer, available=None)
                stock2 = create_stock_from_offer(offer, available=None)
                recommendation = create_recommendation(offer, user)

                deposit = create_deposit(user2, datetime.utcnow(), amount=500)
                booking = create_booking(user2, stock, venue, recommendation, quantity=3)

                PcObject.check_and_save(booking, deposit, user, offer, stock, stock2, user2, user_offerer)

            # when
                response = TestClient().with_auth(email='user@test.com').get(API_URL + f'/offers?')

            # then
                response_json = response.json()
                pprint(response_json)
                assert response.status_code == 200
                assert 'stockAlertMessage' in response_json[0]
                assert response_json[0]['stockAlertMessage'] == "illimité"
