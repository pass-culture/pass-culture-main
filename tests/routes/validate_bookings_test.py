import pytest
from datetime import datetime
from urllib.parse import urlencode

from models import PcObject, EventType, ThingType, Deposit
from models.db import db
from tests.conftest import clean_database, TestClient
from tests.test_utils import API_URL, create_thing_offer, create_deposit, create_stock_with_event_offer, create_venue, \
    create_offerer, \
    create_user, create_booking, create_event_offer, \
    create_event_occurrence, create_stock_from_event_occurrence, create_user_offerer
from utils.human_ids import humanize


@pytest.mark.standalone
class Patch:
    class Returns204:
        @clean_database
        def when_user_has_rights(self, app):
            # Given
            user = create_user()
            admin_user = create_user(email='admin@email.fr', password='P@55w0rd')
            offerer = create_offerer()
            user_offerer = create_user_offerer(admin_user, offerer)
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue, price=0)
            booking = create_booking(user, stock, venue=venue)
            PcObject.check_and_save(booking, user_offerer)
            url = API_URL + '/bookings/token/{}'.format(booking.token)

            # When
            response = TestClient().with_auth('admin@email.fr', 'P@55w0rd').patch(url)

            # Then
            assert response.status_code == 204
            db.session.refresh(booking)
            assert booking.isUsed

        @clean_database
        def when_header_is_not_standard_but_request_is_valid(self, app):
            # Given
            user = create_user()
            admin_user = create_user(email='admin@email.fr', password='P@55w0rd')
            offerer = create_offerer()
            user_offerer = create_user_offerer(admin_user, offerer)
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue, price=0)
            booking = create_booking(user, stock, venue=venue)
            PcObject.check_and_save(booking, user_offerer)
            url = API_URL + '/bookings/token/{}'.format(booking.token)

            # When
            response = TestClient().with_auth('admin@email.fr', 'P@55w0rd',
                                              headers={'origin': 'http://random_header.fr'}).patch(url)

            # Then
            assert response.status_code == 204
            db.session.refresh(booking)
            assert booking.isUsed

        @clean_database
        def when_booking_user_email_has_special_character_url_encoded(self, app):
            # Given
            user = create_user(email='user+plus@email.fr')
            user_admin = create_user(email='admin@email.fr', password='P@55w0rd')
            offerer = create_offerer()
            user_offerer = create_user_offerer(user_admin, offerer, is_admin=True)
            venue = create_venue(offerer)
            offer = create_event_offer(venue, event_name='Event Name')
            event_occurrence = create_event_occurrence(offer)
            stock = create_stock_from_event_occurrence(event_occurrence, price=0)
            booking = create_booking(user, stock, venue=venue)

            PcObject.check_and_save(user_offerer, booking, event_occurrence)
            url_email = urlencode({'email': 'user+plus@email.fr'})
            url = API_URL + '/bookings/token/{}?{}'.format(booking.token, url_email)

            # When
            response = TestClient().with_auth('admin@email.fr', 'P@55w0rd').patch(url)
            # Then
            assert response.status_code == 204

        @clean_database
        def when_user_patching_is_global_admin_is_activation_event_and_no_deposit_for_booking_user(self, app):
            # Given
            user = create_user(is_admin=False, can_book_free_offers=False)
            pro_user = create_user(email='pro@email.fr', password='P@55w0rd', is_admin=True, can_book_free_offers=False)
            offerer = create_offerer()
            user_offerer = create_user_offerer(pro_user, offerer)
            venue = create_venue(offerer)
            activation_offer = create_event_offer(venue, event_type=EventType.ACTIVATION)
            activation_event_occurrence = create_event_occurrence(activation_offer)
            stock = create_stock_from_event_occurrence(activation_event_occurrence, price=0)
            booking = create_booking(user, stock, venue=venue)
            PcObject.check_and_save(booking, user_offerer)
            url = API_URL + '/bookings/token/{}'.format(booking.token)

            # When
            response = TestClient().with_auth('pro@email.fr', 'P@55w0rd').patch(url)

            # Then
            db.session.refresh(user)
            assert response.status_code == 204
            assert user.canBookFreeOffers
            deposits_for_user = Deposit.query.filter_by(userId=user.id).all()
            assert len(deposits_for_user) == 1
            assert deposits_for_user[0].amount == 500
            assert user.canBookFreeOffers

        @clean_database
        def when_user_patching_is_global_admin_is_activation_thing_and_no_deposit_for_booking_user(self, app):
            # Given
            user = create_user(is_admin=False, can_book_free_offers=False)
            pro_user = create_user(email='pro@email.fr', password='P@55w0rd', is_admin=True, can_book_free_offers=False)
            offerer = create_offerer()
            user_offerer = create_user_offerer(pro_user, offerer)
            venue = create_venue(offerer)
            activation_offer = create_thing_offer(venue, thing_type=ThingType.ACTIVATION)
            activation_event_occurrence = create_event_occurrence(activation_offer)
            stock = create_stock_from_event_occurrence(activation_event_occurrence, price=0)
            booking = create_booking(user, stock, venue=venue)
            PcObject.check_and_save(booking, user_offerer)
            url = API_URL + '/bookings/token/{}'.format(booking.token)

            # When
            response = TestClient().with_auth('pro@email.fr', 'P@55w0rd').patch(url)

            # Then
            db.session.refresh(user)
            assert response.status_code == 204
            assert user.canBookFreeOffers
            deposits_for_user = Deposit.query.filter_by(userId=user.id).all()
            assert len(deposits_for_user) == 1
            assert deposits_for_user[0].amount == 500
            assert user.canBookFreeOffers

    class Returns403:
        @clean_database
        def when_user_not_editor_and_valid_email(self, app):
            # Given
            user = create_user()
            admin_user = create_user(email='admin@email.fr', password='P@55w0rd')
            offerer = create_offerer()
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue, price=0)
            booking = create_booking(user, stock, venue=venue)
            PcObject.check_and_save(booking, admin_user)
            url = API_URL + '/bookings/token/{}?email={}'.format(booking.token, user.email)

            # When
            response = TestClient().with_auth('admin@email.fr', 'P@55w0rd').patch(url)

            # Then
            assert response.status_code == 403
            assert response.json()['global'] == ["Cette structure n'est pas enregistr\u00e9e chez cet utilisateur."]
            db.session.refresh(booking)
            assert not booking.isUsed

        @clean_database
        def when_it_is_an_offer_on_an_activation_event_and_user_patching_is_not_global_admin(self, app):
            # Given
            user = create_user()
            pro_user = create_user(email='pro@email.fr', password='P@55w0rd', is_admin=False)
            offerer = create_offerer()
            user_offerer = create_user_offerer(pro_user, offerer)
            venue = create_venue(offerer)
            activation_offer = create_event_offer(venue, event_type=EventType.ACTIVATION)
            activation_event_occurrence = create_event_occurrence(activation_offer)
            stock = create_stock_from_event_occurrence(activation_event_occurrence, price=0)
            booking = create_booking(user, stock, venue=venue)
            PcObject.check_and_save(booking, user_offerer)
            url = API_URL + '/bookings/token/{}'.format(booking.token)

            # When
            response = TestClient().with_auth('pro@email.fr', 'P@55w0rd').patch(url)

            # Then
            assert response.status_code == 403

    class Returns404:
        @clean_database
        def when_user_not_editor_and_invalid_email(self, app):
            # Given
            user = create_user()
            admin_user = create_user(email='admin@email.fr', password='P@55w0rd')
            offerer = create_offerer()
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue, price=0)
            booking = create_booking(user, stock, venue=venue)
            PcObject.check_and_save(booking, admin_user)
            url = API_URL + '/bookings/token/{}?email={}'.format(booking.token, 'wrong@email.fr')

            # When
            response = TestClient().with_auth('admin@email.fr', 'P@55w0rd').patch(url)

            # Then
            assert response.status_code == 404
            db.session.refresh(booking)
            assert booking.isUsed == False

        @clean_database
        def when_booking_user_email_with_special_character_not_url_encoded(self, app):
            # Given
            user = create_user(email='user+plus@email.fr')
            user_admin = create_user(email='admin@email.fr', password='P@55w0rd')
            offerer = create_offerer()
            user_offerer = create_user_offerer(user_admin, offerer, is_admin=True)
            venue = create_venue(offerer)
            offer = create_event_offer(venue, event_name='Event Name')
            event_occurrence = create_event_occurrence(offer)
            stock = create_stock_from_event_occurrence(event_occurrence, price=0)
            booking = create_booking(user, stock, venue=venue)

            PcObject.check_and_save(user_offerer, booking, event_occurrence)
            url = API_URL + '/bookings/token/{}?email={}'.format(booking.token, user.email)

            # When
            response = TestClient().with_auth('admin@email.fr', 'P@55w0rd').patch(url)
            # Then
            assert response.status_code == 404

        @clean_database
        def when_user_not_editor_and_valid_email_but_invalid_offer_id(self, app):
            # Given
            user = create_user()
            admin_user = create_user(email='admin@email.fr', password='P@55w0rd')
            offerer = create_offerer()
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue, price=0)
            booking = create_booking(user, stock, venue=venue)
            PcObject.check_and_save(booking, admin_user)
            url = API_URL + '/bookings/token/{}?email={}&offer_id={}'.format(booking.token, user.email, humanize(123))

            # When
            response = TestClient().with_auth('admin@email.fr', 'P@55w0rd').patch(url)

            # Then
            assert response.status_code == 404
            db.session.refresh(booking)
            assert not booking.isUsed

    class Returns405:
        @clean_database
        def when_user_patching_is_global_admin_is_activation_offer_and_existing_deposit_for_booking_user(
                self,
                app):
            # Given
            user = create_user(is_admin=False, can_book_free_offers=False)
            pro_user = create_user(email='pro@email.fr', password='P@55w0rd', is_admin=True, can_book_free_offers=False)
            offerer = create_offerer()
            user_offerer = create_user_offerer(pro_user, offerer)
            venue = create_venue(offerer)
            activation_offer = create_event_offer(venue, event_type=EventType.ACTIVATION)
            activation_event_occurrence = create_event_occurrence(activation_offer)
            stock = create_stock_from_event_occurrence(activation_event_occurrence, price=0)
            booking = create_booking(user, stock, venue=venue)
            deposit = create_deposit(user, datetime.utcnow(), amount=500)
            PcObject.check_and_save(booking, user_offerer, deposit)
            url = API_URL + '/bookings/token/{}'.format(booking.token)

            # When
            response = TestClient().with_auth('pro@email.fr', 'P@55w0rd').patch(url)

            # Then
            deposits_for_user = Deposit.query.filter_by(userId=user.id).all()
            assert response.status_code == 405
            assert len(deposits_for_user) == 1
            assert deposits_for_user[0].amount == 500

    class Returns410:
        @clean_database
        def when_booking_is_cancelled(self, app):
            # Given
            user = create_user()
            admin_user = create_user(email='admin@email.fr', password='P@55w0rd')
            offerer = create_offerer()
            user_offerer = create_user_offerer(admin_user, offerer)
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue, price=0)
            booking = create_booking(user, stock, venue=venue)
            booking.isCancelled = True
            PcObject.check_and_save(booking, user_offerer)
            url = API_URL + '/bookings/token/{}'.format(booking.token)

            # When
            response = TestClient().with_auth('admin@email.fr', 'P@55w0rd').patch(url)

            # Then
            assert response.status_code == 410
            assert response.json()['booking'] == ['Cette réservation a été annulée']
            db.session.refresh(booking)
            assert not booking.isUsed

        @clean_database
        def when_booking_already_validated(self, app):
            # Given
            user = create_user()
            admin_user = create_user(email='admin@email.fr', password='P@55w0rd')
            offerer = create_offerer()
            user_offerer = create_user_offerer(admin_user, offerer)
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue, price=0)
            booking = create_booking(user, stock, venue=venue)
            booking.isUsed = True
            PcObject.check_and_save(booking, user_offerer)
            url = API_URL + '/bookings/token/{}'.format(booking.token)

            # When
            response = TestClient().with_auth('admin@email.fr', 'P@55w0rd').patch(url)

            # Then
            assert response.status_code == 410
            assert response.json()['booking'] == ['Cette réservation a déjà été validée']
            db.session.refresh(booking)
            assert booking.isUsed
