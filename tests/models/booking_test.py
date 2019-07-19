from datetime import datetime, timedelta

from models import Booking, Offer, Stock, User, Product
from tests.test_utils import create_product_with_thing_type


def test_booking_completed_url_gets_normalized():
    # Given

    product = Product()
    product.url = 'javascript:alert("plop")'

    offer = Offer()
    offer.id = 1
    offer.product = product

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


class BookingIsCancellableTest:
    def test_booking_on_event_with_begining_date_in_more_than_72_hours_is_cancellable(self):
        # Given
        booking = Booking()
        booking.stock = Stock()
        booking.stock.beginningDatetime = datetime.utcnow() + timedelta(hours=73)

        # When
        is_cancellable = booking.isUserCancellable

        # Then
        assert is_cancellable

    def test_booking_on_thing_is_cancellable(self):
        # Given
        booking = Booking()
        booking.stock = Stock()
        booking.stock.offer = Offer()
        booking.stock.offer.product = create_product_with_thing_type()

        # When
        is_cancellable = booking.isUserCancellable

        # Then
        assert is_cancellable == True

    def test_booking_on_event_is_not_cancellable_if_begining_date_time_before_72_hours(self):
        # Given
        booking = Booking()
        booking.stock = Stock()
        booking.stock.beginningDatetime = datetime.utcnow() + timedelta(hours=71)

        # When
        is_cancellable = booking.isUserCancellable

        # Then
        assert is_cancellable == False


class StatusLabelTest:
    def test_is_cancelled_label_when_booking_is_cancelled(self):
        # Given
        booking = Booking()
        booking.stock = Stock()
        booking.isCancelled = True

        # When
        statusLabel = booking.statusLabel

        # Then
        assert statusLabel == "Réservation annulée"

    def test_is_countermak_validated_label_when_booking_is_used(self):
        # Given
        booking = Booking()
        booking.stock = Stock()
        booking.isUsed = True

        # When
        statusLabel = booking.statusLabel

        # Then
        assert statusLabel == 'Contremarque validée'

    def test_validated_label_when_event_is_expired(self):
        # Given
        booking = Booking()
        booking.stock = Stock()
        booking.stock.beginningDatetime = datetime.utcnow() + timedelta(-1)

        # When
        statusLabel = booking.statusLabel

        # Then
        assert statusLabel == 'Validé'
