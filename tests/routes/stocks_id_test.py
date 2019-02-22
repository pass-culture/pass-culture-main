from datetime import timedelta

import pytest

from models.pc_object import PcObject
from tests.conftest import clean_database, TestClient
from utils.human_ids import humanize
from tests.test_utils import API_URL, create_booking, create_user, create_user_offerer, create_offerer, create_venue, create_stock_with_event_offer


@pytest.mark.standalone
class Get:
    class Returns200:
        @clean_database
        def when_user_is_admin(self, app):
            # given
            user = create_user(email='test@email.com', can_book_free_offers=False, password='P@55w0rd', is_admin=True)
            offerer = create_offerer()
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue, price=10, available=10)
            PcObject.check_and_save(user, stock)
            humanized_stock_id = humanize(stock.id)

            # when
            request = TestClient().with_auth('test@email.com', 'P@55w0rd').get(API_URL + '/stocks/' + humanized_stock_id)
            # then
            assert request.status_code == 200
            assert request.json()['available'] == 10
            assert request.json()['price'] == 10


    class Returns404:
        @clean_database
        def when_stock_is_soft_deleted(self, app):
            # given
            user = create_user(email='test@email.com', can_book_free_offers=False, password='P@55w0rd', is_admin=True)
            offerer = create_offerer()
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue, price=10, available=10, is_soft_deleted=True)
            PcObject.check_and_save(user, stock)
            humanized_stock_id = humanize(stock.id)

            # when
            request = TestClient().with_auth('test@email.com', 'P@55w0rd').get(API_URL + '/stocks/' + humanized_stock_id)

            # then
            assert request.status_code == 404


@pytest.mark.standalone
class Patch:
    class Returns200:
        @clean_database
        def when_user_has_editor_rights_on_offerer(self, app):
            # given
            user = create_user(email='test@email.com', password='P@55w0rd')
            offerer = create_offerer()
            user_offerer = create_user_offerer(user, offerer)
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue, price=10, available=10)
            PcObject.check_and_save(user, user_offerer, stock)
            humanized_stock_id = humanize(stock.id)

            # when
            request_update = TestClient().with_auth('test@email.com', 'P@55w0rd').patch(API_URL + '/stocks/' + humanized_stock_id, json={'available': 5, 'price': 20})

            # then
            assert request_update.status_code == 200
            request_after_update = TestClient().with_auth('test@email.com', 'P@55w0rd').get(API_URL + '/stocks/' + humanized_stock_id)
            assert request_after_update.json()['available'] == 5
            assert request_after_update.json()['price'] == 20

        @clean_database
        def when_user_is_admin(self, app):
            # given
            user = create_user(email='test@email.com', can_book_free_offers=False, password='P@55w0rd', is_admin=True)
            offerer = create_offerer()
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue, price=10, available=10)
            PcObject.check_and_save(user, stock)
            humanized_stock_id = humanize(stock.id)

            # when
            request_update = TestClient().with_auth('test@email.com', 'P@55w0rd').patch(API_URL + '/stocks/' + humanized_stock_id, json={'available': 5, 'price': 20})

            # then
            assert request_update.status_code == 200
            request_after_update = TestClient().with_auth('test@email.com', 'P@55w0rd').get(API_URL + '/stocks/' + humanized_stock_id)
            assert request_after_update.json()['available'] == 5
            assert request_after_update.json()['price'] == 20


    class Returns400:
        @clean_database
        def when_wrong_type_for_available(self, app):
            # given
            user = create_user()
            user_admin = create_user(email='email@test.com', can_book_free_offers=False, password='P@55w0rd', is_admin=True)
            offerer = create_offerer()
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue, price=0)
            stock.available = 1
            booking = create_booking(user, stock, venue, recommendation=None)
            PcObject.check_and_save(booking, user_admin)

            # when
            response = TestClient().with_auth('email@test.com', 'P@55w0rd').patch(API_URL + '/stocks/' + humanize(stock.id), json={'available': ' '})

            # then
            assert response.status_code == 400
            assert response.json()['available'] == ['Saisissez un nombre valide']

        @clean_database
        def when_booking_limit_datetime_after_event_occurrence(self, app):
            # given
            from models.pc_object import serialize
            user = create_user(email='email@test.com', can_book_free_offers=False, password='P@55w0rd', is_admin=True)
            offerer = create_offerer()
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue)
            PcObject.check_and_save(stock, user)

            stockId = stock.id

            serialized_date = serialize(stock.eventOccurrence.beginningDatetime + timedelta(days=1))
            # when
            response = TestClient().with_auth('email@test.com', 'P@55w0rd').patch(API_URL + '/stocks/' + humanize(stockId), json={'bookingLimitDatetime': serialized_date})

            # then
            assert response.status_code == 400
            assert response.json()['bookingLimitDatetime'] == [
                'La date limite de réservation pour cette offre est postérieure à la date de début de l\'évènement'
            ]

        @clean_database
        def when_available_below_number_of_already_existing_bookings(self, app):
            # given
            user = create_user()
            user_admin = create_user(email='email@test.com', can_book_free_offers=False, password='P@55w0rd', is_admin=True)
            offerer = create_offerer()
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue, price=0)
            stock.available = 1
            booking = create_booking(user, stock, venue, recommendation=None)
            PcObject.check_and_save(booking, user_admin)

            # when
            response = TestClient().with_auth('email@test.com', 'P@55w0rd').patch(API_URL + '/stocks/' + humanize(stock.id), json={'available': 0})

            # then
            assert response.status_code == 400
            assert 'available' in response.json()


    class Returns403:
        @clean_database
        def when_user_has_no_rights(self, app):
            # given
            user = create_user(email='test@email.com', password='P@55w0rd')
            offerer = create_offerer()
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue)
            PcObject.check_and_save(user, stock)

            # when
            response = TestClient().with_auth('test@email.com', 'P@55w0rd').patch(API_URL + '/stocks/' + humanize(stock.id), json={'available': 5})

            # then
            assert response.status_code == 403
            assert 'Cette structure n\'est pas enregistrée chez cet utilisateur.' in response.json()['global']
