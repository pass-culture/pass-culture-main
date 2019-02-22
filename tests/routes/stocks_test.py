from datetime import timedelta

import pytest

from models import Stock
from models.db import db
from models.pc_object import PcObject, serialize
from tests.conftest import clean_database, TestClient
from utils.human_ids import dehumanize, humanize
from tests.test_utils import API_URL, create_user, create_offerer, create_venue, \
    create_stock_with_event_offer, create_booking, create_event_offer, create_user_offerer, create_event_occurrence, \
    create_recommendation, create_stock_from_event_occurrence

@pytest.mark.standalone
class Get:
    class Returns200:
        @clean_database
        def when_user_is_admin(self, app):
            # Given
            user = create_user(email='test@email.com', can_book_free_offers=False, password='P@55w0rd', is_admin=True)
            offerer = create_offerer()
            venue = create_venue(offerer)
            stock_1 = create_stock_with_event_offer(offerer, venue, price=10, available=10)
            stock_2 = create_stock_with_event_offer(offerer, venue, price=20, available=5)
            stock_3 = create_stock_with_event_offer(offerer, venue, price=15, available=1)
            PcObject.check_and_save(user, stock_1, stock_2, stock_3)

            # When
            request = TestClient().with_auth('test@email.com', 'P@55w0rd').get(API_URL + '/stocks')

            # Then
            assert request.status_code == 200
            stocks = request.json()
            assert len(stocks) == 3

@pytest.mark.standalone
class Post:
    class Returns201:
        @clean_database
        def when_user_has_rights(self, app):
            # Given
            user = create_user(email='test@email.fr', password='P@55w0rd')
            offerer = create_offerer()
            user_offerer = create_user_offerer(user, offerer)
            venue = create_venue(offerer)
            offer = create_event_offer(venue)
            PcObject.check_and_save(user_offerer, offer)

            stock_data = {'price': 1222, 'offerId': humanize(offer.id)}
            PcObject.check_and_save(user)

            # When
            r_create = TestClient().with_auth('test@email.fr', 'P@55w0rd').post(API_URL + '/stocks/', json=stock_data)

            # Then
            assert r_create.status_code == 201
            id = r_create.json()['id']

            stock = Stock.query.filter_by(id=dehumanize(id)).first()
            assert stock.price == 1222


    class Returns400:
        @clean_database
        def when_missing_event_occurrence_id_or_offer_id(self, app):
            # Given
            user = create_user(email='test@email.fr', can_book_free_offers=False, password='P@55w0rd', is_admin=True)
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_event_offer(venue)
            event_occurrence = create_event_occurrence(offer)
            PcObject.check_and_save(user, event_occurrence)

            stock_data = {'price': 1222}
            PcObject.check_and_save(user)

            # When
            response = TestClient().with_auth('test@email.fr', 'P@55w0rd').post(API_URL + '/stocks/', json=stock_data)

            # Then
            assert response.status_code == 400
            r_create_json = response.json()
            assert r_create_json["offerId"] == ["cette entrée est obligatoire en absence de eventOccurrenceId"]
            assert r_create_json["eventOccurrenceId"] == ["cette entrée est obligatoire en absence de offerId"]

        @clean_database
        def when_booking_limit_datetime_after_event_occurrence_beginning_datetime(self, app):
            # Given
            from models.pc_object import serialize
            user = create_user(email='email@test.com', can_book_free_offers=False, password='P@55w0rd', is_admin=True)
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_event_offer(venue)
            event_occurrence = create_event_occurrence(offer)
            PcObject.check_and_save(user, event_occurrence)
            data = {
                'price': 1222,
                'eventOccurrenceId': humanize(event_occurrence.id),
                'bookingLimitDatetime': serialize(event_occurrence.beginningDatetime + timedelta(days=1))
            }

            # When
            response = TestClient().with_auth('email@test.com', 'P@55w0rd').post(API_URL + '/stocks/', json=data)

            # Then
            assert response.status_code == 400
            assert response.json()['bookingLimitDatetime'] == [
                'La date limite de réservation pour cette offre est postérieure à la date de début de l\'évènement'
            ]

        @clean_database
        def when_invalid_format_for_booking_limit_datetime(self, app):
            # Given
            user = create_user(email='test@email.fr', can_book_free_offers=False, password='P@55w0rd', is_admin=True)
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_event_offer(venue)
            event_occurrence = create_event_occurrence(offer)
            PcObject.check_and_save(user, event_occurrence)
            one_hour_before_event = event_occurrence.beginningDatetime - timedelta(hours=1)
            stock_data = {
                'price': 0,
                'offerId': humanize(offer.id),
                'eventOccurrenceId': humanize(event_occurrence.id),
                'bookingLimitDatetime':
                    {
                        'bookingLimitDatetime': serialize(one_hour_before_event)
                    }
                }
            PcObject.check_and_save(user)

             # When
            response = TestClient().with_auth('test@email.fr', 'P@55w0rd').post(API_URL + '/stocks/', json=stock_data)

             # Then
            assert response.status_code == 400
            r_create_json = response.json()
            assert r_create_json["bookingLimitDatetime"] == ["Format de date invalide"]


    class Returns403:
        @clean_database
        def when_user_has_no_rights_and_creating_stock_from_offer_id(self, app):
            # Given
            user = create_user(email='test@email.fr', password='P@55w0rd')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_event_offer(venue)
            PcObject.check_and_save(user, offer)

            stock_data = {'price': 1222, 'offerId': humanize(offer.id)}
            PcObject.check_and_save(user)

            # When
            response = TestClient().with_auth('test@email.fr', 'P@55w0rd').post(API_URL + '/stocks/', json=stock_data)

            # Then
            assert response.status_code == 403
            assert response.json()["global"] == ["Cette structure n'est pas enregistrée chez cet utilisateur."]

        @clean_database
        def when_user_has_no_rights_and_creating_stock_from_event_occurrence(self, app):
            # Given
            user = create_user(email='test@email.fr', password='P@55w0rd')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_event_offer(venue)
            event_occurrence = create_event_occurrence(offer)
            PcObject.check_and_save(user, event_occurrence)

            stock_data = {'price': 1222, 'eventOccurrenceId': humanize(event_occurrence.id)}
            PcObject.check_and_save(user)

            # When
            response = TestClient().with_auth('test@email.fr', 'P@55w0rd').post(API_URL + '/stocks/', json=stock_data)

            # Then
            assert response.status_code == 403
            assert response.json()["global"] == ["Cette structure n'est pas enregistrée chez cet utilisateur."]

@pytest.mark.standalone
class Delete:
    class Returns200:
        @clean_database
        def when_user_is_admin(self, app):
            # Given
            user = create_user(email='email@test.fr', can_book_free_offers=False, password='P@55w0rd', is_admin=True)
            offerer = create_offerer()
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue)
            PcObject.check_and_save(user, stock)

            # When
            r_delete = TestClient().with_auth('email@test.fr', 'P@55w0rd').delete(API_URL + '/stocks/' + humanize(stock.id))

            # Then
            assert r_delete.status_code == 200
            assert r_delete.json()['isSoftDeleted'] is True

            db.session.refresh(stock)
            assert stock
            assert stock.isSoftDeleted

        @clean_database
        def when_user_has_editor_right_on_offerer_cancels_bookings(self, app):
            # Given
            user1 = create_user(email='user1@test.fr')
            user2 = create_user(email='user2@test.fr')
            user_admin = create_user(email='email@test.fr', password='P@55w0rd')
            offerer = create_offerer()
            user_offerer = create_user_offerer(user_admin, offerer)
            venue = create_venue(offerer)
            offer = create_event_offer(venue)
            event_occurrence = create_event_occurrence(offer)
            stock1 = create_stock_from_event_occurrence(event_occurrence, price=0, available=10)
            stock2 = create_stock_from_event_occurrence(event_occurrence, price=0, available=10)
            recommendation1 = create_recommendation(offer, user1)
            recommendation2 = create_recommendation(offer, user2)
            booking1 = create_booking(user1, stock1, venue, recommendation=recommendation1)
            booking2 = create_booking(user1, stock2, venue, recommendation=recommendation1)
            booking3 = create_booking(user2, stock1, venue, recommendation=recommendation2)

            PcObject.check_and_save(booking1, booking2, booking3, user_offerer)

            # When
            response = TestClient().with_auth('email@test.fr', 'P@55w0rd').delete(API_URL + '/stocks/' + humanize(stock1.id))

            # Then
            assert response.status_code == 200
            db.session.refresh(booking1)
            db.session.refresh(booking2)
            db.session.refresh(booking3)
            assert booking1.isCancelled == True
            assert booking2.isCancelled == False
            assert booking3.isCancelled == True


    class Returns403:
        @clean_database
        def when_user_has_no_rights(self, app):
            # Given
            user = create_user(email='email@test.fr', password='P@55w0rd')
            offerer = create_offerer()
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue)
            PcObject.check_and_save(user, stock)

            # When
            response = TestClient().with_auth('email@test.fr', 'P@55w0rd').delete(API_URL + '/stocks/' + humanize(stock.id))

            # Then
            assert response.status_code == 403
            assert 'Cette structure n\'est pas enregistrée chez cet utilisateur.' in response.json()['global']
