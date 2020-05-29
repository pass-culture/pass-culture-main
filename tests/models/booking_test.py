from datetime import datetime, timedelta
from unittest.mock import patch

import pytest

from models import BookingSQLEntity, Offer, StockSQLEntity, UserSQLEntity, Product, ApiErrors
from repository import repository
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_booking, create_user, create_stock, create_offerer, \
    create_venue, \
    create_recommendation, create_mediation, create_deposit
from tests.model_creators.specific_creators import create_stock_from_offer, create_product_with_thing_type, \
    create_product_with_event_type, create_offer_with_thing_product, create_offer_with_event_product, \
    create_stock_with_thing_offer, create_stock_with_event_offer

EVENT_AUTOMATIC_REFUND_DELAY_FOR_TEST = timedelta(hours=72)


def test_booking_completed_url_gets_normalized():
    # Given
    product = Product()

    offer = Offer()
    offer.id = 1
    offer.product = product
    offer.url = 'http://javascript:alert("plop")?token={token}&email={email}'

    stock = StockSQLEntity()

    user = UserSQLEntity()
    user.email = 'bob@example.com'

    booking = BookingSQLEntity()
    booking.token = 'ABCDEF'
    booking.stock = stock
    booking.stock.offer = offer
    booking.user = user

    # When
    completed_url = booking.completedUrl

    # Then
    assert completed_url == 'http://javascript:alert("plop")?token=ABCDEF&email=bob@example.com'


@clean_database
def test_raises_error_on_booking_when_total_stock_is_less_than_bookings_count(app):
    # Given
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer = create_offer_with_thing_product(venue)
    stock = create_stock_from_offer(offer, price=0, quantity=1)
    user1 = create_user(email='used_booking@example.com')
    user2 = create_user(email='booked@example.com')

    booking1 = create_booking(user=user1,
                              stock=stock)

    repository.save(booking1)

    booking2 = create_booking(user=user2,
                              stock=stock)
    # When
    with pytest.raises(ApiErrors) as e:
        repository.save(booking2)

    # Then
    assert e.value.errors['global'] == ['La quantité disponible pour cette offre est atteinte.']


@clean_database
def test_raises_error_on_booking_when_existing_booking_is_used_and_booking_date_is_after_last_update_on_stock(app):
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer = create_offer_with_thing_product(venue)
    stock = create_stock_from_offer(offer, price=0, quantity=1)
    user1 = create_user(email='used_booking@example.com')
    user2 = create_user(email='booked@example.com')
    repository.save(stock)
    date_after_stock_last_update = datetime.utcnow()
    booking1 = create_booking(user=user1,
                              stock=stock,
                              date_used=date_after_stock_last_update,
                              is_cancelled=False,
                              is_used=True)
    repository.save(booking1)
    date_after_last_booking = datetime.utcnow()
    booking2 = create_booking(user=user2,
                              stock=stock,
                              date_used=date_after_last_booking,
                              is_cancelled=False,
                              is_used=False)

    # When
    with pytest.raises(ApiErrors) as e:
        repository.save(booking2)

    # Then
    assert e.value.errors['global'] == ['La quantité disponible pour cette offre est atteinte.']


class BookingThumbUrlTest:
    @patch('models.has_thumb_mixin.get_storage_base_url', return_value='http://localhost/storage')
    def test_model_thumbUrl_should_use_mediation_of_recommendation_first_as_thumbUrl(self, get_storage_base_url):
        # given
        user = create_user(email='user@example.com')
        offerer = create_offerer()
        venue = create_venue(offerer)
        product = create_product_with_event_type(thumb_count=1)
        offer = create_offer_with_event_product(product=product, venue=venue)
        mediation = create_mediation(offer=offer, idx=1, thumb_count=1)
        stock = create_stock(quantity=1, offer=offer, price=12)
        recommendation = create_recommendation(idx=100, mediation=mediation, offer=offer, user=user)
        recommendation.mediationId = mediation.id

        # when
        booking = create_booking(user=user, recommendation=recommendation, stock=stock, venue=venue)

        # then
        assert booking.thumbUrl == "http://localhost/storage/thumbs/mediations/AE"

    @patch('models.has_thumb_mixin.get_storage_base_url', return_value='http://localhost/storage')
    def test_model_thumbUrl_should_have_thumbUrl_using_active_mediation_when_no_recommendation(self,
                                                                                               get_storage_base_url):
        # given
        user = create_user(email='user@example.com')
        offerer = create_offerer()
        venue = create_venue(offerer)
        product = create_product_with_event_type()
        offer = create_offer_with_event_product(product=product, venue=venue)
        inactive_mediation = create_mediation(offer=offer, is_active=False, idx=1, thumb_count=1)
        active_mediation = create_mediation(offer=offer, idx=2, thumb_count=1)
        stock = create_stock(quantity=1, offer=offer, price=12)

        # when
        booking = create_booking(user=user, stock=stock, venue=venue)

        # then
        assert booking.thumbUrl == "http://localhost/storage/thumbs/mediations/A9"

    @patch('models.has_thumb_mixin.get_storage_base_url', return_value='http://localhost/storage')
    def test_model_thumbUrl_should_have_thumbUrl_using_product_when_no_mediation_nor_recommendation(self,
                                                                                                    get_storage_base_url):
        # given
        user = create_user(email='user@example.com')
        offerer = create_offerer()
        venue = create_venue(offerer)
        product = create_product_with_event_type(thumb_count=1)
        product.id = 2
        offer = create_offer_with_event_product(product=product, venue=venue)
        stock = create_stock(quantity=1, offer=offer, price=12)

        # when
        booking = create_booking(user=user, stock=stock, venue=venue)

        # then
        assert booking.thumbUrl == "http://localhost/storage/thumbs/products/A9"

    @patch('models.has_thumb_mixin.get_storage_base_url', return_value='http://localhost/storage')
    def test_model_thumbUrl_should_have_no_thumb_when_no_mediation_nor_recommendation_and_product_thumb_count_is_0(self,
                                                                                                                   get_storage_base_url):
        # given
        user = create_user(email='user@example.com')
        offerer = create_offerer()
        venue = create_venue(offerer)
        product = create_product_with_event_type(thumb_count=0)
        offer = create_offer_with_event_product(product=product, venue=venue)
        stock = create_stock(quantity=1, offer=offer, price=12)

        # when
        booking = create_booking(user=user, stock=stock, venue=venue)

        # then
        assert booking.thumbUrl is None

    @patch('models.has_thumb_mixin.get_storage_base_url', return_value='http://localhost/storage')
    def test_model_thumbUrl_should_have_no_thumb_when_no_thumb_on_mediation_nor_recommendation_and_mediation_thumb_count_is_0(
            self, get_storage_base_url):
        # given
        user = create_user(email='user@example.com')
        offerer = create_offerer()
        venue = create_venue(offerer)
        product = create_product_with_event_type(thumb_count=0)
        offer = create_offer_with_event_product(product=product, venue=venue)
        mediation = create_mediation(offer=offer, idx=1, thumb_count=0)
        stock = create_stock(quantity=1, offer=offer, price=12)
        recommendation = create_recommendation(idx=100, mediation=mediation, offer=offer, user=user)
        recommendation.mediationId = mediation.id

        # when
        booking = create_booking(user=user, recommendation=recommendation, stock=stock, venue=venue)

        # then
        assert booking.thumbUrl is None


class BookingEventOfferQRCodeGenerationTest:
    def test_model_qrcode_should_return_qrcode_as_base64_string_when_booking_is_not_used_and_not_cancelled(self):
        # given
        two_days_after_now = datetime.utcnow() + timedelta(days=2)
        user = create_user()
        product = create_product_with_event_type()
        offer = create_offer_with_event_product(product=product)
        stock = create_stock(beginning_datetime=two_days_after_now, offer=offer)

        # when
        booking = create_booking(stock=stock, user=user, is_used=False, is_cancelled=False)

        # then
        assert type(booking.qrCode) is str

    def test_model_qrcode_should_return_qrcode_as_None_when_booking_is_used_and_cancelled(self):
        # given
        two_days_after_now = datetime.utcnow() + timedelta(days=2)
        user = create_user()
        product = create_product_with_event_type()
        offer = create_offer_with_event_product(product=product)
        stock = create_stock(beginning_datetime=two_days_after_now, offer=offer)

        # when
        booking = create_booking(stock=stock, user=user, is_used=True, is_cancelled=True)

        # then
        assert booking.qrCode is None

    def test_model_qrcode_should_return_qrcode_as_None_when_booking_is_used_and_expired_and_not_cancelled(self):
        # given
        yesterday = datetime.utcnow() - timedelta(days=1)
        user = create_user()
        product = create_product_with_event_type()
        offer = create_offer_with_event_product(product=product)
        stock = create_stock(beginning_datetime=yesterday, offer=offer)

        # when
        booking = create_booking(stock=stock, user=user, is_used=True, is_cancelled=False)

        # then
        assert booking.qrCode is None

    def test_model_qrcode_should_return_qrcode_as_base64_string_when_event_booking_is_used_and_not_expired_and_not_cancelled(
            self):
        # given
        two_days_after_now = datetime.utcnow() + timedelta(days=2)
        user = create_user()
        product = create_product_with_event_type()
        offer = create_offer_with_event_product(product=product)
        stock = create_stock(beginning_datetime=two_days_after_now, offer=offer)

        # when
        booking = create_booking(stock=stock, user=user, is_used=True, is_cancelled=False)

        # then
        assert type(booking.qrCode) is str

    def test_model_qrcode_should_return_qrcode_as_None_when_booking_is_used_and_expired_and_cancelled(self):
        # given
        yesterday = datetime.utcnow() - timedelta(days=1)
        user = create_user()
        product = create_product_with_event_type()
        offer = create_offer_with_event_product(product=product)
        stock = create_stock(beginning_datetime=yesterday, offer=offer)

        # when
        booking = create_booking(stock=stock, user=user, is_used=True, is_cancelled=True)

        # then
        assert booking.qrCode is None

    def test_model_qrcode_should_return_qrcode_as_base64_string_when_event_booking_is_used_and_not_expired_and_cancelled(
            self):
        # given
        two_days_after_now = datetime.utcnow() + timedelta(days=2)
        user = create_user()
        product = create_product_with_event_type()
        offer = create_offer_with_event_product(product=product)
        stock = create_stock(beginning_datetime=two_days_after_now, offer=offer)

        # when
        booking = create_booking(stock=stock, user=user, is_used=True, is_cancelled=True)

        # then
        assert booking.qrCode is None


class BookingThingOfferQRCodeGenerationTest:
    def test_model_qrcode_should_return_qrcode_as_base64_string_when_booking_is_not_used_and_not_cancelled(self):
        # given
        user = create_user()
        product = create_product_with_thing_type()
        venue = create_venue(offerer=create_offerer())
        offer = create_offer_with_thing_product(product=product, venue=venue)
        stock = create_stock(offer=offer)

        # when
        booking = create_booking(stock=stock, user=user, is_used=False, is_cancelled=False)

        # then
        assert type(booking.qrCode) is str

    def test_model_qrcode_should_return_qrcode_as_base64_string_when_thing_booking_is_not_used_and_not_cancelled(self):
        # given
        user = create_user()
        product = create_product_with_thing_type()
        venue = create_venue(offerer=create_offerer())
        offer = create_offer_with_thing_product(product=product, venue=venue)
        stock = create_stock(offer=offer)

        # when
        booking = create_booking(stock=stock, user=user, is_used=False, is_cancelled=False)

        # then
        assert type(booking.qrCode) is str

    def test_model_qrcode_should_return_qrcode_as_None_when_booking_is_used_and_cancelled(self):
        # given
        user = create_user()
        product = create_product_with_thing_type()
        venue = create_venue(offerer=create_offerer())
        offer = create_offer_with_thing_product(product=product, venue=venue)
        stock = create_stock(offer=offer)

        # when
        booking = create_booking(stock=stock, user=user, is_used=True, is_cancelled=True)

        # then
        assert booking.qrCode is None

    def test_model_qrcode_should_return_qrcode_as_None_when_booking_is_used_and_not_cancelled(self):
        # given
        user = create_user()
        product = create_product_with_thing_type()
        venue = create_venue(offerer=create_offerer())
        offer = create_offer_with_thing_product(product=product, venue=venue)
        stock = create_stock(offer=offer)

        # when
        booking = create_booking(stock=stock, user=user, is_used=True, is_cancelled=False)

        # then
        assert booking.qrCode is None

    def test_model_qrcode_should_return_qrcode_as_None_when_booking_is_not_used_and_is_cancelled(self):
        # given
        user = create_user()
        product = create_product_with_thing_type()
        venue = create_venue(offerer=create_offerer())
        offer = create_offer_with_thing_product(product=product, venue=venue)
        stock = create_stock(offer=offer)

        # when
        booking = create_booking(stock=stock, user=user, is_used=False, is_cancelled=True)

        # then
        assert booking.qrCode is None


class BookingIsCancellableTest:
    def test_booking_on_event_with_begining_date_in_more_than_72_hours_is_cancellable(self):
        # Given
        booking = BookingSQLEntity()
        booking.stock = StockSQLEntity()
        booking.stock.beginningDatetime = datetime.utcnow() + timedelta(hours=73)

        # When
        is_cancellable = booking.isUserCancellable

        # Then
        assert is_cancellable

    def test_booking_on_thing_is_cancellable(self):
        # Given
        booking = BookingSQLEntity()
        booking.stock = StockSQLEntity()
        booking.stock.offer = Offer()
        booking.stock.offer.product = create_product_with_thing_type()

        # When
        is_cancellable = booking.isUserCancellable

        # Then
        assert is_cancellable == True

    def test_booking_on_event_is_not_cancellable_if_begining_date_time_before_72_hours(self):
        # Given
        booking = BookingSQLEntity()
        booking.stock = StockSQLEntity()
        booking.stock.beginningDatetime = datetime.utcnow() + timedelta(hours=71)

        # When
        is_cancellable = booking.isUserCancellable

        # Then
        assert is_cancellable == False


class BookingCancellationDateTest:
    @clean_database
    def test_should_fill_cancellation_date_when_booking_is_cancelled(self, app):
        # Given
        user = create_user()
        booking = create_booking(user=user, amount=1, is_cancelled=True)

        # When
        repository.save(booking)

        # Then
        updated_booking = BookingSQLEntity.query.first()
        assert updated_booking.isCancelled
        assert updated_booking.cancellationDate is not None

    @clean_database
    def test_should_clear_cancellation_date_when_booking_is_not_cancelled(self, app):
        # Given
        user = create_user()
        create_deposit(user=user, amount=100)
        booking = create_booking(user=user, amount=1, is_cancelled=True)
        repository.save(booking)

        # When
        booking.isCancelled = False
        repository.save(booking)

        # Then
        updated_booking = BookingSQLEntity.query.first()
        assert updated_booking.isCancelled is False
        assert updated_booking.cancellationDate is None

    @clean_database
    def test_should_not_update_cancellation_date_when_updating_another_attribute(self, app):
        # Given
        user = create_user()
        booking = create_booking(user=user, amount=1, is_cancelled=True)
        repository.save(booking)
        original_cancellation_date = booking.cancellationDate

        # When
        booking.quantity = 2
        repository.save(booking)

        # Then
        updated_booking = BookingSQLEntity.query.first()
        assert updated_booking.isCancelled is True
        assert updated_booking.cancellationDate == original_cancellation_date


class IsEventExpiredTest:
    def test_is_not_expired_when_stock_is_not_an_event(self):
        # Given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        stock = create_stock_with_thing_offer(offerer=offerer, venue=venue)
        booking = create_booking(user=user, stock=stock)

        # When
        is_event_expired = booking.isEventExpired

        # Then
        assert is_event_expired is False

    def test_is_not_expired_when_stock_is_an_event_in_the_future(self):
        # Given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        three_days_from_now = datetime.utcnow() + timedelta(hours=72)
        stock = create_stock_with_event_offer(offerer=offerer, venue=venue,
                                              beginning_datetime=three_days_from_now)
        booking = create_booking(user=user, stock=stock)

        # When
        is_event_expired = booking.isEventExpired

        # Then
        assert is_event_expired is False

    def test_is_expired_when_stock_is_an_event_in_the_past(self):
        # Given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        one_day_in_the_past = datetime.utcnow() - timedelta(hours=24)
        stock = create_stock_with_event_offer(offerer=offerer, venue=venue,
                                              beginning_datetime=one_day_in_the_past)
        booking = create_booking(user=user, stock=stock)

        # When
        is_event_expired = booking.isEventExpired

        # Then
        assert is_event_expired is True


class IsEventDeletableTest:
    @patch('models.stock_sql_entity.EVENT_AUTOMATIC_REFUND_DELAY', EVENT_AUTOMATIC_REFUND_DELAY_FOR_TEST)
    def test_is_deletable_when_stock_is_not_an_event(self):
        # Given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        stock = create_stock_with_thing_offer(offerer=offerer, venue=venue)
        booking = create_booking(user=user, stock=stock)

        # When
        is_event_deletable = booking.isEventDeletable

        # Then
        assert is_event_deletable is True

    @patch('models.stock_sql_entity.EVENT_AUTOMATIC_REFUND_DELAY', EVENT_AUTOMATIC_REFUND_DELAY_FOR_TEST)
    def test_is_deletable_when_stock_is_an_event_in_the_future(self):
        # Given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        three_days_from_now = datetime.utcnow() + timedelta(hours=72)
        stock = create_stock_with_event_offer(offerer=offerer, venue=venue,
                                              beginning_datetime=three_days_from_now)
        booking = create_booking(user=user, stock=stock)

        # When
        is_event_deletable = booking.isEventDeletable

        # Then
        assert is_event_deletable is True

    @patch('models.stock_sql_entity.EVENT_AUTOMATIC_REFUND_DELAY', EVENT_AUTOMATIC_REFUND_DELAY_FOR_TEST)
    def test_is_deletable_when_stock_is_expired_since_less_than_event_automatic_refund_delay(self):
        # Given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        expired_date_but_not_automaticaly_refunded = datetime.utcnow() - EVENT_AUTOMATIC_REFUND_DELAY_FOR_TEST + timedelta(1)
        stock = create_stock_with_event_offer(offerer=offerer, venue=venue,
                                              beginning_datetime=expired_date_but_not_automaticaly_refunded)
        booking = create_booking(user=user, stock=stock)

        # When
        is_event_deletable = booking.isEventDeletable

        # Then
        assert is_event_deletable is True

    @patch('models.stock_sql_entity.EVENT_AUTOMATIC_REFUND_DELAY', EVENT_AUTOMATIC_REFUND_DELAY_FOR_TEST)
    def test_is_not_deletable_when_stock_is_expired_since_more_than_event_automatic_refund_delay(self):
        # Given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        expired_date_and_automaticaly_refunded = datetime.utcnow() - EVENT_AUTOMATIC_REFUND_DELAY_FOR_TEST
        stock = create_stock_with_event_offer(offerer=offerer, venue=venue,
                                              beginning_datetime=expired_date_and_automaticaly_refunded)
        booking = create_booking(user=user, stock=stock)

        # When
        is_event_deletable = booking.isEventDeletable

        # Then
        assert is_event_deletable is False
