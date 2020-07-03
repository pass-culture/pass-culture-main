from datetime import datetime, timedelta

import pytest

from domain.booking.booking import Booking
from domain.booking.booking_exceptions import EventHappensInLessThan72Hours, BookingIsAlreadyUsed
from tests.domain_creators.generic_creators import create_domain_stock, create_domain_beneficiary


class TotalAmountTest:
    def test_should_return_total_amount(self) -> None:
        # Given
        beneficiary = create_domain_beneficiary()
        stock = create_domain_stock(
            identifier=1,
            quantity=2,
            offer=None,
            price=1.2,
            beginning_datetime=None,
            booking_limit_datetime=None,
            is_soft_deleted=False,
            bookings=[]
        )
        booking = Booking(beneficiary=beneficiary, stock=stock, amount=1.2, quantity=2, is_cancelled=False)

        # When
        total_amount = booking.total_amount

        # Then
        assert total_amount == 2.4


class CancelTest:
    def should_raise_error_when_booking_is_used(self) -> None:
        # Given
        beneficiary = create_domain_beneficiary()
        stock = create_domain_stock(
            identifier=1,
            quantity=2,
            offer=None,
            price=1.2,
            beginning_datetime=None,
            booking_limit_datetime=None,
            is_soft_deleted=False,
            bookings=[]
        )
        booking = Booking(beneficiary=beneficiary, stock=stock, amount=1.2, quantity=2, is_cancelled=False,
                          is_used=True)

        # When
        with pytest.raises(BookingIsAlreadyUsed) as error:
            booking.cancel()

        # Then
        assert error.value.errors['booking'] == ['Impossible d\'annuler une réservation consommée']
        assert booking.isCancelled is False

    def should_raise_error_when_booking_linked_on_stock_event_with_beginning_date_in_less_than_72_hours(self) -> None:
        # Given
        tomorrow = datetime.now() + timedelta(days=1)
        beneficiary = create_domain_beneficiary()
        stock = create_domain_stock(
            identifier=1,
            quantity=2,
            offer=None,
            price=1.2,
            beginning_datetime=tomorrow,
            booking_limit_datetime=None,
            is_soft_deleted=False,
            bookings=[]
        )
        booking = Booking(beneficiary=beneficiary, stock=stock, amount=1.2, quantity=2, is_cancelled=False, is_used=False)

        # When
        with pytest.raises(EventHappensInLessThan72Hours) as error:
            booking.cancel()

        # Then
        assert error.value.errors[
                   'booking'] == ["Impossible d'annuler une réservation moins de 72h avant le début de l'évènement"]
        assert booking.isCancelled is False

    def should_change_booking_status_to_cancelled_when_its_not_used_or_far_from_event_date(self) -> None:
        # Given
        beneficiary = create_domain_beneficiary()
        stock = create_domain_stock(
            identifier=1,
            quantity=2,
            offer=None,
            price=1.2,
            beginning_datetime=None,
            booking_limit_datetime=None,
            is_soft_deleted=False,
            bookings=[]
        )
        booking = Booking(beneficiary=beneficiary, stock=stock, amount=1.2, quantity=2, is_cancelled=False, is_used=False)

        # When
        booking.cancel()

        # Then
        assert booking.isCancelled is True
