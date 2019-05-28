from datetime import timedelta, datetime

import pytest

from models import Stock
from models.db import db
from models.pc_object import PcObject, serialize
from tests.conftest import clean_database, TestClient
from tests.test_utils import API_URL, create_user, create_offerer, create_venue, \
    create_stock_with_event_offer, create_booking, create_offer_with_event_product, create_user_offerer, create_event_occurrence, \
    create_recommendation, create_stock_from_event_occurrence, create_stock_with_event_offer, create_stock_with_thing_offer, \
    create_offer_with_thing_product
from utils.human_ids import dehumanize, humanize



@pytest.mark.standalone
class Get:
    class Returns200:
        @clean_database
        def when_user_is_admin(self, app):
            # Given
            user = create_user(email='test@email.com', can_book_free_offers=False, is_admin=True)
            offerer = create_offerer()
            venue = create_venue(offerer)
            stock_1 = create_stock_with_event_offer(offerer, venue, price=10, available=10)
            stock_2 = create_stock_with_event_offer(offerer, venue, price=20, available=5)
            stock_3 = create_stock_with_event_offer(offerer, venue, price=15, available=1)
            PcObject.save(user, stock_1, stock_2, stock_3)

            # When
            request = TestClient().with_auth('test@email.com').get(API_URL + '/stocks')

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
            user = create_user(email='test@email.fr')
            offerer = create_offerer()
            user_offerer = create_user_offerer(user, offerer)
            venue = create_venue(offerer)
            offer = create_offer_with_thing_product(venue)
            PcObject.save(user_offerer, offer)

            stock_data = {'price': 1222, 'offerId': humanize(offer.id)}
            PcObject.save(user)

            # When
            response = TestClient().with_auth('test@email.fr')\
                .post(API_URL + '/stocks/', json=stock_data)

            # Then
            assert response.status_code == 201
            id = response.json()['id']

            stock = Stock.query.filter_by(id=dehumanize(id)).first()
            assert stock.price == 1222


        @clean_database
        def when_booking_limit_datetime_is_none_for_thing(self, app):
            # Given
            user = create_user(email='test@email.fr', can_book_free_offers=False, is_admin=True)
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_thing_product(venue)
            PcObject.save(user, offer)

            data = {
                'price': 0,
                'offerId': humanize(offer.id),
                'bookingLimitDatetime': None
            }

            # When
            response = TestClient().with_auth(user.email) \
                .post(API_URL + '/stocks/', json=data)

            # Then
            assert response.status_code == 201
            assert response.json()["price"] == 0
            assert response.json()["bookingLimitDatetime"] is None
            
            id = response.json()['id']            
            stock = Stock.query.filter_by(id=dehumanize(id)).first()
            assert stock.price == 0
            assert stock.bookingLimitDatetime is None

    
    class Returns400:
        @clean_database
        def when_missing_offer_id(self, app):
            # Given
            user = create_user(email='test@email.fr', can_book_free_offers=False, is_admin=True)
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_thing_product(venue)
            PcObject.save(user, offer)

            # When
            response = TestClient().with_auth(user.email) \
                .post(API_URL + '/stocks/', json={'price': 1222})

            # Then
            assert response.status_code == 400
            assert response.json()["offerId"] == ['Ce paramètre est obligatoire']

        @clean_database
        def when_booking_limit_datetime_after_beginning_datetime(self, app):
            # Given
            user = create_user(email='email@test.com', can_book_free_offers=False, is_admin=True)
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue)
            PcObject.save(user, offer)

            beginningDatetime = datetime(2019, 2, 14)

            data = {
                'price': 1222,
                'offerId': humanize(offer.id),
                'beginningDatetime': serialize(beginningDatetime),
                'endDatetime': serialize(beginningDatetime + timedelta(days=1)),
                'bookingLimitDatetime': serialize(beginningDatetime + timedelta(days=2))
            }

            # When
            response = TestClient().with_auth(user.email) \
                .post(API_URL + '/stocks/', json=data)

            # Then
            assert response.status_code == 400
            assert response.json()['bookingLimitDatetime'] == [
                'La date limite de réservation pour cette offre est postérieure à la date de début de l\'évènement'
            ]

        @clean_database
        def when_invalid_format_for_booking_limit_datetime(self, app):
            # Given
            user = create_user(email='test@email.fr', can_book_free_offers=False, is_admin=True)
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_thing_product(venue)
            PcObject.save(user, offer)

            data = {
                'price': 0,
                'offerId': humanize(offer.id),
                'bookingLimitDatetime': 'zbbopbjeo'
            }

            # When
            response = TestClient().with_auth(user.email) \
                .post(API_URL + '/stocks/', json=data)

            # Then
            assert response.status_code == 400
            assert response.json()["bookingLimitDatetime"] == ["Format de date invalide"]


        @clean_database
        def when_booking_limit_datetime_is_none_for_event(self, app):
            # Given
            beginningDatetime = datetime(2019, 2, 14)
            user = create_user(email='test@email.fr', can_book_free_offers=False, is_admin=True)
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue)
            PcObject.save(user, offer)

            data = {
                'price': 0,
                'offerId': humanize(offer.id),
                'bookingLimitDatetime': None,
                'beginningDatetime': serialize(beginningDatetime),
                'endDatetime': serialize(beginningDatetime + timedelta(days=1)),
            }

            # When
            response = TestClient().with_auth(user.email) \
                .post(API_URL + '/stocks/', json=data)

            # Then
            assert response.status_code == 400
            assert response.json()["bookingLimitDatetime"] == ['Ce paramètre est obligatoire']


        @clean_database
        def when_setting_beginning_and_end_datetimes_on_offer_with_thing(self, app):
            # Given
            user = create_user(email='test@email.fr', can_book_free_offers=False, is_admin=True)
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_thing_product(venue)
            PcObject.save(user, offer)
            beginningDatetime = datetime(2019, 2, 14)

            data = {
                'price': 0,
                'offerId': humanize(offer.id),
                'beginningDatetime': serialize(beginningDatetime),
                'endDatetime': serialize(beginningDatetime + timedelta(days=1)),
                'bookingLimitDatetime': serialize(beginningDatetime - timedelta(days=2))
            }

            # When
            response = TestClient().with_auth(user.email) \
                .post(API_URL + '/stocks/', json=data)

            # Then
            assert response.status_code == 400
            assert response.json()['global'] == [
                'Impossible de mettre des dates de début et fin si l\'offre ne porte pas sur un évenement'
            ]


    class Returns403:
        @clean_database
        def when_user_has_no_rights_and_creating_stock_from_offer_id(self, app):
            # Given
            user = create_user(email='test@email.fr')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_thing_product(venue)
            PcObject.save(user, offer)

            data = {'price': 1222, 'offerId': humanize(offer.id)}

            # When
            response = TestClient().with_auth(user.email) \
                .post(API_URL + '/stocks/', json=data)

            # Then
            assert response.status_code == 403
            assert response.json()["global"] == ["Cette structure n'est pas enregistrée chez cet utilisateur."]


@pytest.mark.standalone
class Delete:
    class Returns200:
        @clean_database
        def when_user_is_admin(self, app):
            # Given
            user = create_user(email='email@test.fr', can_book_free_offers=False, is_admin=True)
            offerer = create_offerer()
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue)
            PcObject.save(user, stock)

            # When
            response = TestClient().with_auth('email@test.fr').delete(API_URL + '/stocks/' + humanize(stock.id))

            # Then
            assert response.status_code == 200
            assert response.json()['isSoftDeleted'] is True

            db.session.refresh(stock)
            assert stock
            assert stock.isSoftDeleted

        @clean_database
        def when_user_has_editor_right_on_offerer_cancels_bookings(self, app):
            # Given
            user1 = create_user(email='user1@test.fr')
            user2 = create_user(email='user2@test.fr')
            user_admin = create_user(email='email@test.fr')
            offerer = create_offerer()
            user_offerer = create_user_offerer(user_admin, offerer)
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue)
            event_occurrence = create_event_occurrence(offer)
            stock1 = create_stock_from_event_occurrence(event_occurrence, price=0, available=10)
            stock2 = create_stock_from_event_occurrence(event_occurrence, price=0, available=10)
            recommendation1 = create_recommendation(offer, user1)
            recommendation2 = create_recommendation(offer, user2)
            booking1 = create_booking(user1, stock1, venue, recommendation=recommendation1)
            booking2 = create_booking(user1, stock2, venue, recommendation=recommendation1)
            booking3 = create_booking(user2, stock1, venue, recommendation=recommendation2)

            PcObject.save(booking1, booking2, booking3, user_offerer)

            # When
            response = TestClient().with_auth('email@test.fr').delete(API_URL + '/stocks/' + humanize(stock1.id))

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
            user = create_user(email='email@test.fr')
            offerer = create_offerer()
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue)
            PcObject.save(user, stock)

            # When
            response = TestClient().with_auth('email@test.fr').delete(API_URL + '/stocks/' + humanize(stock.id))

            # Then
            assert response.status_code == 403
            assert 'Cette structure n\'est pas enregistrée chez cet utilisateur.' in response.json()['global']


@pytest.mark.standalone
class Patch:
    class Returns200:
        @clean_database
        def when_user_is_admin(self, app):
            # Given
            user = create_user(email='email@test.fr', can_book_free_offers=False, is_admin=True)
            offerer = create_offerer()
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue, price=69)
            PcObject.save(user, stock)

            beginningDatetime = datetime(2019, 2, 14)

            data = {
                "dateModified": serialize(beginningDatetime),
                "beginningDatetime": serialize(beginningDatetime),
                "endDatetime": serialize(beginningDatetime + timedelta(days=3)),
                "offerId": humanize(stock.offer.id),
                "price": 1256,
                "available": 20,
                "groupSize": 256,
                "bookingLimitDatetime": serialize(beginningDatetime),
                "bookingRecapSent": serialize(beginningDatetime),
                "price": 666
            }

            # When
            response = TestClient().with_auth('email@test.fr').patch(API_URL + '/stocks/' + humanize(stock.id), json=data)

            # Then
            assert response.status_code == 200
            db.session.refresh(stock)
            assert stock.price == 666


        @clean_database
        def when_booking_limit_datetime_is_none_for_thing(self, app):
            # Given
            user = create_user(email='test@email.fr', can_book_free_offers=False, is_admin=True)
            offerer = create_offerer()
            venue = create_venue(offerer)
            stock = create_stock_with_thing_offer(offerer, venue)
            PcObject.save(user, stock)

            data = {
                'price': 120,
                'offerId': humanize(stock.offer.id),
                'bookingLimitDatetime': None
            }

            # When
            response = TestClient().with_auth(user.email) \
                .patch(API_URL + '/stocks/' + humanize(stock.id), json=data)

            # Then
            assert response.status_code == 200
            db.session.refresh(stock)
            assert stock.price == 120


    class Returns400:
        @clean_database
        def when_booking_limit_datetime_is_none_for_event(self, app):
            # Given
            user = create_user(email='test@email.fr', can_book_free_offers=False, is_admin=True)
            offerer = create_offerer()
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue)
            PcObject.save(user, stock)

            data = {
                'price': 0,
                'offerId': humanize(stock.offer.id),
                'bookingLimitDatetime': None
            }

            # When
            response = TestClient().with_auth(user.email) \
                .patch(API_URL + '/stocks/' + humanize(stock.id), json=data)

            # Then
            assert response.status_code == 400
            assert response.json()["bookingLimitDatetime"] == ['Ce paramètre est obligatoire']


    class Returns403:
        @clean_database
        def when_user_has_no_rights(self, app):
            # Given
            user = create_user(email='email@test.fr')
            offerer = create_offerer()
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue)
            PcObject.save(user, stock)
            beginningDatetime = datetime(2019, 2, 14)

            data = {
                "dateModified": serialize(beginningDatetime),
                "beginningDatetime": serialize(beginningDatetime),
                "endDatetime": serialize(beginningDatetime + timedelta(days=3)),
                "offerId": humanize(stock.offer.id),
                "price": 1256,
                "available": 20,
                "groupSize": 256,
                "bookingLimitDatetime": serialize(beginningDatetime),
                "bookingRecapSent": serialize(beginningDatetime)
            }

            # When
            response = TestClient().with_auth('email@test.fr').patch(API_URL + '/stocks/' + humanize(stock.id), json=data)

            # Then
            assert response.status_code == 403
            assert 'Cette structure n\'est pas enregistrée chez cet utilisateur.' in response.json()['global']

