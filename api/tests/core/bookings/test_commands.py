import datetime

import pytest

import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.bookings import models as bookings_models
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offer_models
from pcapi.models import db

from tests.test_utils import run_command


class ArchiveOldBookingsTest:
    @pytest.mark.usefixtures("clean_database")
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
        db.session.commit()
        db.session.close()
        # when
        run_command(app, "archive_old_bookings")

        # then
        old_booking = db.session.get(bookings_models.Booking, old_booking_id)
        recent_booking = db.session.get(bookings_models.Booking, recent_booking_id)
        assert old_booking.displayAsEnded
        assert not recent_booking.displayAsEnded

    @pytest.mark.usefixtures("clean_database")
    @pytest.mark.parametrize(
        "subcategoryId",
        offer_models.Stock.AUTOMATICALLY_USED_SUBCATEGORIES,
    )
    def test_old_subcategories_bookings_are_archived(self, app, subcategoryId):
        # given
        now = datetime.datetime.utcnow()
        recent = now - datetime.timedelta(days=29, hours=23)
        old = now - datetime.timedelta(days=30, hours=1)
        stock_free = offers_factories.StockFactory(
            offer=offers_factories.OfferFactory(subcategoryId=subcategoryId), price=0
        )
        stock_not_free = offers_factories.StockFactory(
            offer=offers_factories.OfferFactory(subcategoryId=subcategoryId), price=10
        )
        recent_booking = bookings_factories.BookingFactory(stock=stock_free, dateCreated=recent)
        old_booking = bookings_factories.BookingFactory(stock=stock_free, dateCreated=old)
        old_not_free_booking = bookings_factories.BookingFactory(stock=stock_not_free, dateCreated=old)
        recent_booking_id = recent_booking.id
        old_booking_id = old_booking.id
        old_not_free_booking_id = old_not_free_booking.id
        db.session.commit()
        db.session.close()

        # when
        run_command(app, "archive_old_bookings")

        # then

        old_booking = db.session.get(bookings_models.Booking, old_booking_id)
        old_not_free_booking = db.session.get(bookings_models.Booking, old_not_free_booking_id)
        recent_booking = db.session.get(bookings_models.Booking, recent_booking_id)
        assert not recent_booking.displayAsEnded
        assert not old_not_free_booking.displayAsEnded
        assert old_booking.displayAsEnded

    @pytest.mark.usefixtures("clean_database")
    @pytest.mark.parametrize(
        "subcategoryId",
        offer_models.Stock.AUTOMATICALLY_USED_SUBCATEGORIES,
    )
    def test_old_subcategories_bookings_are_archived_when_no_longer_free(self, app, subcategoryId, client):
        # given
        now = datetime.datetime.utcnow()
        recent = now - datetime.timedelta(days=29, hours=23)
        old = now - datetime.timedelta(days=30, hours=1)
        offer = offers_factories.ThingOfferFactory(subcategoryId=subcategoryId)
        stock_free = offers_factories.StockFactory(offer=offer, price=0)
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        recent_booking = bookings_factories.BookingFactory(stock=stock_free, dateCreated=recent)
        old_booking = bookings_factories.BookingFactory(stock=stock_free, dateCreated=old)
        recent_booking_id = recent_booking.id
        old_booking_id = old_booking.id
        stock_data = {
            "price": 10,
        }
        client.with_session_auth("user@example.com").post("/stocks/bulk/", json=stock_data)
        db.session.commit()
        db.session.close()

        # when
        run_command(app, "archive_old_bookings")

        # then
        recent_booking = db.session.get(bookings_models.Booking, recent_booking_id)
        old_booking = db.session.get(bookings_models.Booking, old_booking_id)
        assert not recent_booking.displayAsEnded
        assert old_booking.displayAsEnded
