import datetime

from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.bookings import models as bookings_models
from pcapi.core.offers import factories as offers_factories

from tests.conftest import clean_database
from tests.test_utils import run_command


class ArchiveOldDigitalBookingsTest:
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
        run_command(app, "archive_old_activation_code_bookings")

        # then
        old_booking = bookings_models.Booking.query.get(old_booking_id)
        recent_booking = bookings_models.Booking.query.get(recent_booking_id)
        assert old_booking.displayAsEnded
        assert not recent_booking.displayAsEnded
