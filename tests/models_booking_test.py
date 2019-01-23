from datetime import datetime, timedelta

import pytest

from models import Booking, Offer, Stock, Thing, User, EventOccurrence


@pytest.mark.standalone
def test_booking_completed_url_gets_normalized():
    # Given

    thing = Thing()
    thing.url = 'javascript:alert("plop")'

    offer = Offer()
    offer.id = 1
    offer.thing = thing

    stock = Stock()

    user = User()
    user.email = 'bob@bob.com'

    booking = Booking()
    booking.token = 'ABCDEF'
    booking.stock = stock
    booking.stock.offer = offer
    booking.user = user

    # When
    completedUrl = booking.completedUrl

    # Then
    assert completedUrl == 'http://javascript:alert("plop")'


@pytest.mark.standalone
class BookingIsCancellableTest:
    def test_booking_on_event_with_begining_date_in_more_than_72_hours_is_cancellable(self):
        # Given
        booking = Booking()
        booking.stock = Stock()
        booking.stock.eventOccurrence = EventOccurrence()
        booking.stock.eventOccurrence.beginningDatetime = datetime.utcnow() + timedelta(hours=73)

        # When
        is_cancellable = booking.isUserCancellable

        # Then
        assert is_cancellable

    def test_booking_on_thing_is_not_cancellable(self):
        # Given
        booking = Booking()
        booking.stock = Stock()
        booking.stock.offer = Offer()
        booking.stock.offer.thing = Thing()

        # When
        is_cancellable = booking.isUserCancellable

        # Then
        assert is_cancellable == False

    def test_booking_on_event_is_not_cancellable_if_begining_date_time_before_72_hours(self):
        # Given
        booking = Booking()
        booking.stock = Stock()
        booking.stock.eventOccurrence = EventOccurrence()
        booking.stock.eventOccurrence.beginningDatetime = datetime.utcnow() + timedelta(hours=71)

        # When
        is_cancellable = booking.isUserCancellable

        # Then
        assert is_cancellable == False
