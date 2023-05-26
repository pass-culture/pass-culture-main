import datetime

import pytest

from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.bookings import models as bookings_models
from pcapi.core.bookings.constants import FREE_OFFER_SUBCATEGORIES_TO_ARCHIVE
from pcapi.core.offers import factories as offers_factories

from tests.conftest import clean_database
from tests.test_utils import run_command


class ArchiveOldBookingsTest:
    @clean_database
    def test_basics(self, app):
        # given
        now = datetime.datetime.utcnow()
        recent = now - datetime.timedelta(days=29, hours=23)
        old = now - datetime.timedelta(days=30, hours=1)
        offer = offers_factories.OfferFactory(url="http://example.com")
        stock = offers_factories.StockFactory(offer=offer)
        recent_booking = bookings_factories.BookingFactory(stock=stock, dateCreated=recent)
        old_booking = bookings_factories.BookingFactory(stock=stock, dateCreated=old)
        offers_factories.ActivationCodeFactory(booking=recent_booking, stock=stock)
        offers_factories.ActivationCodeFactory(booking=old_booking, stock=stock)
        recent_booking_id = recent_booking.id
        old_booking_id = old_booking.id

        # when
        run_command(app, "archive_old_bookings")

        # then
        old_booking = bookings_models.Booking.query.get(old_booking_id)
        recent_booking = bookings_models.Booking.query.get(recent_booking_id)
        assert old_booking.displayAsEnded
        assert not recent_booking.displayAsEnded

    @clean_database
    @pytest.mark.parametrize(
        "subcategory",
        FREE_OFFER_SUBCATEGORIES_TO_ARCHIVE,
    )
    def test_old_subcategories_bookings_are_archived(self, app, subcategory):
        # given
        now = datetime.datetime.utcnow()
        recent = now - datetime.timedelta(days=29, hours=23)
        old = now - datetime.timedelta(days=30, hours=1)
        stock_free = offers_factories.StockFactory(
            offer=offers_factories.OfferFactory(subcategoryId=subcategory.id), price=0
        )
        stock_not_free = offers_factories.StockFactory(
            offer=offers_factories.OfferFactory(subcategoryId=subcategory.id), price=10
        )
        recent_booking = bookings_factories.BookingFactory(stock=stock_free, dateCreated=recent)
        old_booking = bookings_factories.BookingFactory(stock=stock_free, dateCreated=old)
        old_not_free_booking = bookings_factories.BookingFactory(stock=stock_not_free, dateCreated=old)
        recent_booking_id = recent_booking.id
        old_booking_id = old_booking.id
        old_not_free_booking_id = old_not_free_booking.id

        # when
        run_command(app, "archive_old_bookings")

        # then
        old_booking = bookings_models.Booking.query.get(old_booking_id)
        old_not_free_booking = bookings_models.Booking.query.get(old_not_free_booking_id)
        recent_booking = bookings_models.Booking.query.get(recent_booking_id)
        assert not recent_booking.displayAsEnded
        assert not old_not_free_booking.displayAsEnded
        assert old_booking.displayAsEnded
