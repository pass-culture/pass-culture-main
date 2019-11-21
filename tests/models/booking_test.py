from datetime import datetime, timedelta
from unittest.mock import patch

import pytest

from models import Booking, Offer, Stock, User, Product, PcObject, ApiErrors
from tests.conftest import clean_database
from tests.test_utils import create_product_with_thing_type, create_offerer, create_venue, \
    create_offer_with_thing_product, create_stock_from_offer, create_user, create_booking, \
    create_offer_with_event_product, create_mediation, create_stock, create_recommendation, \
    create_product_with_event_type


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


@clean_database
def test_raises_error_on_booking_when_existing_booking_is_used_and_booking_date_is_after_last_update_on_stock(app):
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer = create_offer_with_thing_product(venue)
    stock = create_stock_from_offer(offer, price=0, available=1)
    user1 = create_user(email='used_booking@booking.com')
    user2 = create_user(email='booked@email.com')
    PcObject.save(stock)
    date_after_stock_last_update = datetime.utcnow()
    booking1 = create_booking(user1,
                              stock,
                              date_used=date_after_stock_last_update,
                              is_cancelled=False,
                              is_used=True)
    PcObject.save(booking1)
    date_after_last_booking = datetime.utcnow()
    booking2 = create_booking(user2,
                              stock,
                              date_used=date_after_last_booking,
                              is_cancelled=False,
                              is_used=False)

    # When
    with pytest.raises(ApiErrors) as e:
        PcObject.save(booking2)

    # Then
    assert e.value.errors['global'] == ['La quantité disponible pour cette offre est atteinte.']


@patch('models.has_thumb_mixin.get_storage_base_url', return_value='http://localhost/storage')
def test_model_thumbUrl_should_use_mediation_first_as_thumbUrl(get_storage_base_url):
    # given
    user = create_user(email='user@test.com')
    offerer = create_offerer()
    venue = create_venue(offerer)
    product = create_product_with_event_type(thumb_count=1)
    offer = create_offer_with_event_product(product=product, venue=venue)
    mediation = create_mediation(offer=offer)
    mediation.id = 1
    stock = create_stock(price=12, available=1, offer=offer)
    recommendation = create_recommendation(idx=100, mediation=mediation, offer=offer, user=user)
    recommendation.mediationId = mediation.id

    # when
    booking = create_booking(recommendation=recommendation, stock=stock, user=user, venue=venue)

    # then
    assert booking.thumbUrl == "http://localhost/storage/thumbs/mediations/AE"


@patch('models.has_thumb_mixin.get_storage_base_url', return_value='http://localhost/storage')
def test_model_thumbUrl_should_have_thumbUrl_using_productId_when_no_mediation(get_storage_base_url):
    # given
    user = create_user(email='user@test.com')
    offerer = create_offerer()
    venue = create_venue(offerer)
    product = create_product_with_event_type(thumb_count=0)
    product.id = 2
    offer = create_offer_with_event_product(product=product, venue=venue)
    stock = create_stock(price=12, available=1, offer=offer)

    # when
    booking = create_booking(recommendation=None, stock=stock, user=user, venue=venue)

    # then
    assert booking.thumbUrl == "http://localhost/storage/thumbs/products/A9"


def test_model_qrCode_should_return_qrCode_as_base64_string_when_booking_is_not_used_and_not_cancelled():
    # given
    user = create_user(email='user@test.com')
    offerer = create_offerer()
    venue = create_venue(offerer)
    product = create_product_with_event_type(thumb_count=0)
    product.id = 2
    offer = create_offer_with_event_product(product=product, venue=venue)
    stock = create_stock(price=12, available=1, offer=offer)

    # when
    booking = create_booking(recommendation=None, stock=stock, user=user, venue=venue, is_used=False,
                             is_cancelled=False)

    # then
    assert booking.qrCode is not None
    assert type(booking.qrCode) is str


def test_model_qrCode_should_return_qrCode_as_None_when_booking_is_used_and_cancelled():
    # given
    user = create_user(email='user@test.com')
    offerer = create_offerer()
    venue = create_venue(offerer)
    product = create_product_with_event_type(thumb_count=0)
    product.id = 2
    offer = create_offer_with_event_product(product=product, venue=venue)
    stock = create_stock(price=12, available=1, offer=offer)

    # when
    booking = create_booking(recommendation=None, stock=stock, user=user, venue=venue, is_used=True, is_cancelled=True)

    # then
    assert booking.qrCode is None


def test_model_qrCode_should_return_qrCode_as_None_when_booking_is_used_and_not_cancelled():
    # given
    user = create_user(email='user@test.com')
    offerer = create_offerer()
    venue = create_venue(offerer)
    product = create_product_with_event_type(thumb_count=0)
    product.id = 2
    offer = create_offer_with_event_product(product=product, venue=venue)
    stock = create_stock(price=12, available=1, offer=offer)

    # when
    booking = create_booking(recommendation=None, stock=stock, user=user, venue=venue, is_used=True, is_cancelled=False)

    # then
    assert booking.qrCode is None


def test_model_qrCode_should_return_qrCode_as_None_when_booking_is_not_used_and_is_cancelled():
    # given
    user = create_user(email='user@test.com')
    offerer = create_offerer()
    venue = create_venue(offerer)
    product = create_product_with_event_type(thumb_count=0)
    product.id = 2
    offer = create_offer_with_event_product(product=product, venue=venue)
    stock = create_stock(price=12, available=1, offer=offer)

    # when
    booking = create_booking(recommendation=None, stock=stock, user=user, venue=venue, is_used=False, is_cancelled=True)

    # then
    assert booking.qrCode is None


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
