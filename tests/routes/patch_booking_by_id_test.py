from datetime import datetime, timedelta

from models import PcObject
from models.db import db
from tests.conftest import clean_database, TestClient
from tests.test_utils import API_URL, create_deposit, create_venue, create_offerer, \
    create_user, create_booking, create_offer_with_event_product, \
    create_event_occurrence, create_stock_from_event_occurrence
from utils.human_ids import humanize


class PatchBookingTest:
    @clean_database
    def test_cannot_cancel_used_booking(self, app):
        # Given
        user = create_user(email='test@email.com')
        deposit_date = datetime.utcnow() - timedelta(minutes=2)
        deposit = create_deposit(user, deposit_date, amount=500)
        booking = create_booking(user, is_used=True)
        PcObject.save(user, deposit, booking)

        # When
        response = TestClient().with_auth(user.email) \
            .patch(API_URL + '/bookings/' + humanize(booking.id), json={"isCancelled": True})

        # Then
        assert response.status_code == 400
        assert response.json()['booking'] == ["Impossible d\'annuler une réservation consommée"]
        db.session.refresh(booking)
        assert not booking.isCancelled

    @clean_database
    def test_returns_400_when_trying_to_patch_something_else_than_is_cancelled(self, app):
        # Given
        user = create_user(email='test@email.com')
        deposit_date = datetime.utcnow() - timedelta(minutes=2)
        deposit = create_deposit(user, deposit_date, amount=500)
        booking = create_booking(user, quantity=1)
        PcObject.save(user, deposit, booking)

        # When
        response = TestClient().with_auth(user.email) \
            .patch(API_URL + '/bookings/' + humanize(booking.id), json={"quantity": 3})

        # Then
        assert response.status_code == 400
        db.session.refresh(booking)
        assert booking.quantity == 1

    @clean_database
    def test_returns_400_when_trying_to_set_is_cancelled_to_false(self, app):
        # Given
        user = create_user(email='test@email.com')
        deposit_date = datetime.utcnow() - timedelta(minutes=2)
        deposit = create_deposit(user, deposit_date, amount=500)
        booking = create_booking(user)
        booking.isCancelled = True
        PcObject.save(user, deposit, booking)

        # When
        response = TestClient().with_auth(user.email) \
            .patch(API_URL + '/bookings/' + humanize(booking.id), json={"isCancelled": False})

        # Then
        assert response.status_code == 400
        db.session.refresh(booking)
        assert booking.isCancelled

    @clean_database
    def test_returns_200_and_effectively_marks_the_booking_as_cancelled_when_valid_usecase(self, app):
        # Given
        in_four_days = datetime.utcnow() + timedelta(days=4)
        in_five_days = datetime.utcnow() + timedelta(days=5)
        user = create_user(email='test@email.com')
        deposit_date = datetime.utcnow() - timedelta(minutes=2)
        deposit = create_deposit(user, deposit_date, amount=500)
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue)
        event_occurrence = create_event_occurrence(offer, beginning_datetime=in_four_days, end_datetime=in_five_days)
        stock = create_stock_from_event_occurrence(event_occurrence)
        booking = create_booking(user, stock, venue)
        PcObject.save(user, deposit, booking)

        # When
        response = TestClient().with_auth(user.email) \
            .patch(API_URL + '/bookings/' + humanize(booking.id), json={"isCancelled": True})

        # Then
        assert response.status_code == 200
        db.session.refresh(booking)
        assert booking.isCancelled

    @clean_database
    def test_returns_400_and_does_not_cancel_booking_when_beginning_date_time_in_less_than_72_hours(self, app):
        # Given
        in_five_days = datetime.utcnow() + timedelta(days=5)
        in_one_days = datetime.utcnow() + timedelta(days=1)
        user = create_user(email='test@email.com')
        deposit_date = datetime.utcnow() - timedelta(minutes=2)
        deposit = create_deposit(user, deposit_date, amount=500)
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue)
        event_occurrence = create_event_occurrence(offer, beginning_datetime=in_one_days, end_datetime=in_five_days)
        stock = create_stock_from_event_occurrence(event_occurrence)
        booking = create_booking(user, stock, venue)
        PcObject.save(user, deposit, booking)

        # When
        response = TestClient().with_auth(user.email) \
            .patch(API_URL + '/bookings/' + humanize(booking.id), json={"isCancelled": True})

        # Then
        assert response.status_code == 400

    @clean_database
    def test_returns_404_if_booking_does_not_exist(self, app):
        # Given
        user = create_user(email='test@email.com')
        PcObject.save(user)

        # When
        response = TestClient().with_auth(user.email) \
            .patch(API_URL + '/bookings/AX', json={"isCancelled": True})

        # Then
        assert response.status_code == 404

    @clean_database
    def test_returns_403_and_does_not_mark_the_booking_as_cancelled_when_cancelling_for_other_user(self, app):
        # Given
        other_user = create_user(email='test2@email.com')
        deposit_date = datetime.utcnow() - timedelta(minutes=2)
        deposit = create_deposit(other_user, deposit_date, amount=500)
        booking = create_booking(other_user)
        user = create_user(email='test@email.com')
        PcObject.save(user, other_user, deposit, booking)

        # When
        response = TestClient().with_auth(user.email) \
            .patch(API_URL + '/bookings/' + humanize(booking.id), json={"isCancelled": True})

        # Then
        assert response.status_code == 403
        db.session.refresh(booking)
        assert not booking.isCancelled

    @clean_database
    def test_returns_200_and_effectively_marks_the_booking_as_cancelled_when_cancelling_for_other_as_admin(self, app):
        # Given
        admin_user = create_user(email='test@email.com', can_book_free_offers=False, is_admin=True)
        other_user = create_user(email='test2@email.com')
        deposit_date = datetime.utcnow() - timedelta(minutes=2)
        deposit = create_deposit(other_user, deposit_date, amount=500)
        booking = create_booking(other_user)
        PcObject.save(admin_user, other_user, deposit, booking)

        # When
        response = TestClient().with_auth(admin_user.email) \
            .patch(API_URL + '/bookings/' + humanize(booking.id), json={"isCancelled": True})

        # Then
        assert response.status_code == 200
        db.session.refresh(booking)
        assert booking.isCancelled
