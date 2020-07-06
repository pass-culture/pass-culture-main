from datetime import datetime
from unittest.mock import patch

from models import BookingSQLEntity
from repository import repository
from scripts.booking.correct_bookings_status import get_bookings_cancelled_during_quarantine_with_payment, \
    correct_booking_status
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_booking, create_stock, create_venue, create_offerer, \
    create_user, create_deposit, create_payment
from tests.model_creators.specific_creators import create_offer_with_event_product


class GetBookingsCancelledDuringQuarantineWithPaymentTest:
    @clean_database
    def test_should_only_return_bookings_with_payment(self, app):
        # Given
        beneficiary = create_user()
        create_deposit(user=beneficiary)
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue)
        stock1 = create_stock(offer=offer, beginning_datetime=datetime(2020, 4, 16))
        stock2 = create_stock(offer=offer, beginning_datetime=datetime(2020, 4, 16))
        booking1 = create_booking(stock=stock1, user=beneficiary, is_cancelled=True)
        booking2 = create_booking(stock=stock2, user=beneficiary, is_cancelled=True)
        payment = create_payment(offerer=offerer, booking=booking1)

        repository.save(payment, booking2)

        # When
        bookings_result = get_bookings_cancelled_during_quarantine_with_payment()

        # Then
        assert bookings_result == [booking1]

    @clean_database
    def test_should_return_cancelled_booking_with_payment(self, app):
        # Given
        beneficiary = create_user()
        create_deposit(user=beneficiary)
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue)
        stock1 = create_stock(offer=offer, beginning_datetime=datetime(2020, 4, 16))
        stock2 = create_stock(offer=offer, beginning_datetime=datetime(2020, 4, 16))
        booking1 = create_booking(stock=stock1, user=beneficiary, is_cancelled=True)
        booking2 = create_booking(stock=stock2, user=beneficiary, is_cancelled=True)
        payment = create_payment(offerer=offerer, booking=booking1)

        repository.save(payment, booking2)

        # When
        bookings_result = get_bookings_cancelled_during_quarantine_with_payment()

        # Then
        assert bookings_result == [booking1]

    @clean_database
    def test_should_not_return_non_cancelled_booking_with_payment(self, app):
        # Given
        beneficiary = create_user()
        create_deposit(user=beneficiary)
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue)
        stock1 = create_stock(offer=offer, beginning_datetime=datetime(2020, 4, 16))
        booking1 = create_booking(stock=stock1, user=beneficiary, is_cancelled=False)
        payment = create_payment(offerer=offerer, booking=booking1)

        repository.save(payment)

        # When
        bookings_result = get_bookings_cancelled_during_quarantine_with_payment()

        # Then
        assert len(bookings_result) == 0

    @clean_database
    def test_should_not_return_booking_in_excluded_list(self, app):
        # Given
        beneficiary = create_user()
        create_deposit(user=beneficiary)
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue)
        stock1 = create_stock(offer=offer, beginning_datetime=datetime(2020, 4, 16))
        booking1 = create_booking(stock=stock1, user=beneficiary, is_cancelled=True, token='2QLYYA')
        payment = create_payment(offerer=offerer, booking=booking1)

        repository.save(payment)

        # When
        bookings_result = get_bookings_cancelled_during_quarantine_with_payment()

        # Then
        assert len(bookings_result) == 0


class CorrectBookingStatusTest:
    @clean_database
    @patch('scripts.booking.correct_bookings_status.get_bookings_cancelled_during_quarantine_with_payment')
    def test_should_revert_booking_cancellation_for_bookings_to_update(self,
                                                                       get_bookings_cancelled_during_quarantine_with_payment,
                                                                       app):
        # Given
        beneficiary = create_user()
        create_deposit(user=beneficiary)
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue)
        stock = create_stock(offer=offer, beginning_datetime=datetime(2020, 4, 16))
        booking = create_booking(stock=stock, user=beneficiary, is_cancelled=True)
        payment = create_payment(offerer=offerer, booking=booking)
        repository.save(payment)

        get_bookings_cancelled_during_quarantine_with_payment.return_value = [booking]

        # When
        correct_booking_status()

        # Then
        corrected_booking = BookingSQLEntity.query.get(booking.id)
        assert corrected_booking.isCancelled is False
        assert corrected_booking.cancellationDate is None
        assert corrected_booking.isUsed is True
        assert corrected_booking.dateUsed == booking.dateCreated

    @clean_database
    @patch('scripts.booking.correct_bookings_status.get_bookings_cancelled_during_quarantine_with_payment')
    def test_should_not_revert_booking_dateused_if_booking_already_has_one(
            self,
            stub_get_bookings_cancelled_during_quarantine_with_payment,
            app):
        # Given
        dateused = datetime(2020, 7, 3, 20, 4, 4)
        beneficiary = create_user()
        create_deposit(user=beneficiary)
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue)
        stock = create_stock(offer=offer, beginning_datetime=datetime(2020, 4, 16))
        booking = create_booking(stock=stock,
                                 user=beneficiary, is_cancelled=True,
                                 date_created=datetime(2019, 7, 3, 20, 4, 4),
                                 date_used=dateused)
        payment = create_payment(offerer=offerer, booking=booking)
        repository.save(payment)

        stub_get_bookings_cancelled_during_quarantine_with_payment.return_value = [booking]

        # When
        correct_booking_status()

        # Then
        corrected_booking = BookingSQLEntity.query.get(booking.id)
        assert corrected_booking.isCancelled is False
        assert corrected_booking.cancellationDate is None
        assert corrected_booking.isUsed is True
        assert corrected_booking.dateUsed == dateused
