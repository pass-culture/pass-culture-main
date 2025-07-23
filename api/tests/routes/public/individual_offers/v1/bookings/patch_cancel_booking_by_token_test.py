import datetime

import pytest
from dateutil.relativedelta import relativedelta

from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.offers import factories as offers_factories

from tests.routes.public.helpers import PublicAPIVenueEndpointHelper


pytestmark = pytest.mark.usefixtures("db_session")


class CancelBookingByTokenTest(PublicAPIVenueEndpointHelper):
    endpoint_url = "/public/bookings/v1/cancel/token/{token}"
    endpoint_method = "patch"
    default_path_params = {"token": "TOKEN"}

    def setup_base_resource(self, venue=None):
        venue = venue or self.setup_venue()
        offer = offers_factories.ThingOfferFactory(
            venue=venue,
            description="Un livre de contrepèterie",
            name="Vieux motard que jamais",
            ean="1234567890123",
        )
        past = datetime.datetime.utcnow() - datetime.timedelta(days=2)
        product_stock = offers_factories.StockFactory(offer=offer, beginningDatetime=past)
        booking = bookings_factories.BookingFactory(
            dateCreated=past - datetime.timedelta(days=2),
            user__email="beneficiary@example.com",
            user__phoneNumber="0101010101",
            user__dateOfBirth=datetime.datetime.utcnow() - relativedelta(years=18, months=2),
            stock=product_stock,
        )
        return offer, booking

    def test_should_raise_404_because_has_no_access_to_venue(self):
        plain_api_key, _ = self.setup_provider()
        _, booking = self.setup_base_resource()
        response = self.make_request(plain_api_key, {"token": booking.token})
        assert response.status_code == 404

    def test_should_raise_404_because_venue_provider_is_inactive(self):
        plain_api_key, venue_provider = self.setup_inactive_venue_provider()
        _, booking = self.setup_base_resource(venue=venue_provider.venue)
        response = self.make_request(plain_api_key, {"token": booking.token})
        assert response.status_code == 404

    def test_key_has_rights_and_regular_product_offer(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        _, booking = self.setup_base_resource(venue=venue_provider.venue)

        response = self.make_request(plain_api_key, {"token": booking.token})

        assert response.status_code == 204
        assert booking.status is BookingStatus.CANCELLED

    def test_key_has_rights_and_regular_event_offer(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        offer = offers_factories.EventOfferFactory(
            venue=venue_provider.venue,
            description="Un livre de contrepèterie",
            name="Vieux motard que jamais",
        )
        yesterday = datetime.datetime.utcnow() - datetime.timedelta(days=1)
        in_3_days = datetime.datetime.utcnow() + datetime.timedelta(days=3)
        stock = offers_factories.EventStockFactory(offer=offer, beginningDatetime=in_3_days)
        booking = bookings_factories.BookingFactory(
            dateCreated=yesterday,
            user__email="beneficiary@example.com",
            user__phoneNumber="0101010101",
            user__dateOfBirth=datetime.datetime.utcnow() - relativedelta(years=18, months=2),
            stock=stock,
        )

        response = self.make_request(plain_api_key, {"token": booking.token})

        assert response.status_code == 204
        assert booking.status == BookingStatus.CANCELLED

    @pytest.mark.parametrize(
        "stock_date_beginning,booking_date_created",
        [
            (
                # booking are not cancellable less than 48h before the event
                datetime.datetime.utcnow() + datetime.timedelta(hours=36),  # less than 48h from now
                datetime.datetime.utcnow() - datetime.timedelta(days=1),  # yesterday
            ),
            (  # after 2 days, event booking are not cancellable
                datetime.datetime.utcnow() + datetime.timedelta(weeks=1),  # in 1 week
                datetime.datetime.utcnow() - datetime.timedelta(days=2),  # 2 days ago
            ),
        ],
    )
    def test_should_raise_due_to_constraint_on_dates(self, stock_date_beginning, booking_date_created):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        offer = offers_factories.EventOfferFactory(venue=venue_provider.venue)
        stock = offers_factories.EventStockFactory(offer=offer, beginningDatetime=stock_date_beginning)
        booking = bookings_factories.BookingFactory(stock=stock, dateCreated=booking_date_created)

        response = self.make_request(plain_api_key, {"token": booking.token})

        assert response.json == {"booking": "This booking cannot be cancelled anymore"}
        assert response.status_code == 403

    @pytest.mark.parametrize(
        "booking_factory,expected_status_code,expected_error_json",
        [
            (bookings_factories.ReimbursedBookingFactory, 403, {"payment": "This booking has been reimbursed"}),
            (bookings_factories.CancelledBookingFactory, 410, {"booking": "This booking has already been cancelled"}),
            (bookings_factories.UsedBookingFactory, 410, {"booking": "This booking has been validated"}),
        ],
    )
    def test_should_raise_due_to_booking_status(self, booking_factory, expected_status_code, expected_error_json):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        offer = offers_factories.ThingOfferFactory(venue=venue_provider.venue)
        stock = offers_factories.StockFactory(offer=offer)
        booking = booking_factory(stock=stock)

        response = self.make_request(plain_api_key, {"token": booking.token})

        assert response.status_code == expected_status_code
        assert response.json == expected_error_json
