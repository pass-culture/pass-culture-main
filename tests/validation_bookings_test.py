from datetime import datetime, timedelta

import pytest

from models import Booking, ApiErrors, Stock, EventOccurrence, Offer, Thing
from validation.bookings import check_booking_is_cancellable


@pytest.mark.standalone
def test_check_booking_is_cancellable_raises_api_error_when_used_booking():
    # Given
    booking = Booking()
    booking.isUsed = True

    # When
    with pytest.raises(ApiErrors) as e:
        check_booking_is_cancellable(booking, is_user_cancellation=False)

    # Then
    assert e.value.errors['booking'] == ["Impossible d\'annuler une réservation consommée"]


@pytest.mark.standalone
def test_check_booking_is_cancellable_raises_api_error_when_user_cancellation_and_event_in_less_than_48h():
    # Given
    booking = Booking()
    booking.isUsed = False
    booking.stock = Stock()
    booking.stock.eventOccurrence = EventOccurrence()
    booking.stock.eventOccurrence.beginningDatetime = datetime.utcnow() + timedelta(hours=24)

    # When
    with pytest.raises(ApiErrors) as e:
        check_booking_is_cancellable(booking, is_user_cancellation=True)

    # Then
    assert e.value.errors['booking'] == [
        "Impossible d\'annuler une réservation moins de 48h avant le début de l'évènement"]


@pytest.mark.standalone
def test_check_booking_is_cancellable_does_not_raise_api_error_when_offerer_cancellation_and_event_in_less_than_48h():
    # Given
    booking = Booking()
    booking.isUsed = False
    booking.stock = Stock()
    booking.stock.eventOccurrence = EventOccurrence()
    booking.stock.eventOccurrence.beginningDatetime = datetime.utcnow() + timedelta(hours=24)

    # When
    check_output = check_booking_is_cancellable(booking, is_user_cancellation=False)

    # Then
    assert check_output is None


@pytest.mark.standalone
def test_check_booking_is_cancellable_does_not_raise_api_error_when_user_cancellation_not_used_and_thing():
    # Given
    booking = Booking()
    booking.isUsed = False
    booking.stock = Stock()
    booking.stock.offer = Offer()
    booking.stock.offer.thing = Thing()

    # When
    check_output = check_booking_is_cancellable(booking, is_user_cancellation=False)

    # Then
    assert check_output is None
