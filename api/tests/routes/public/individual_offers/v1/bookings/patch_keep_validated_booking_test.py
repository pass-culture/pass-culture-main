import datetime

import pytest
from dateutil.relativedelta import relativedelta

from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.offers import factories as offers_factories

from tests.routes.public.helpers import PublicAPIVenueEndpointHelper


pytestmark = pytest.mark.usefixtures("db_session")


class PatchKeepBookingByTokenTest(PublicAPIVenueEndpointHelper):
    endpoint_url = "/public/bookings/v1/keep/token/{token}"
    endpoint_method = "patch"
    default_path_params = {"token": "T0K3N"}

    def setup_base_resource(self, venue=None, status=None):
        venue = venue or self.setup_venue()
        offer = offers_factories.ThingOfferFactory(
            venue=venue,
            description="Un livre de contrepèterie",
            name="Vieux motard que jamais",
            ean="1234567890123",
        )
        past = datetime.datetime.utcnow() - datetime.timedelta(days=2)
        stock = offers_factories.StockFactory(offer=offer, beginningDatetime=past)
        booking = bookings_factories.BookingFactory(
            dateCreated=past - datetime.timedelta(days=2),
            user__email="beneficiary@example.com",
            user__phoneNumber="0101010101",
            user__dateOfBirth=datetime.datetime.utcnow() - relativedelta(years=18, months=2),
            stock=stock,
            dateUsed=datetime.datetime.utcnow() - datetime.timedelta(days=1),
            status=status or BookingStatus.USED,
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

    def test_key_has_rights_and_regular_offer(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        _, booking = self.setup_base_resource(venue=venue_provider.venue)

        response = self.make_request(plain_api_key, {"token": booking.token})

        assert response.status_code == 204
        assert booking.status is BookingStatus.CONFIRMED

    def test_should_raise_403_when_booking_is_refunded(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        _, booking = self.setup_base_resource(venue=venue_provider.venue, status=BookingStatus.REIMBURSED)

        response = self.make_request(plain_api_key, {"token": booking.token})

        assert response.status_code == 403
        assert response.json == {"payment": "This booking has been reimbursed"}
        assert booking.status is BookingStatus.REIMBURSED

    def test_should_raise_403_when_booking_is_not_used(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        _, booking = self.setup_base_resource(venue=venue_provider.venue, status=BookingStatus.CONFIRMED)

        response = self.make_request(plain_api_key, {"token": booking.token})

        assert response.status_code == 403
        assert response.json == {"booking": "This booking has not been used"}
        assert booking.status is BookingStatus.CONFIRMED

    def test_should_raise_403_when_stock_is_event_and_booking_is_not_confirmed_yet(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        offer = offers_factories.EventOfferFactory(venue=venue_provider.venue)
        stock = offers_factories.StockFactory(
            offer=offer, bookingLimitDatetime=datetime.datetime.utcnow() + datetime.timedelta(days=10)
        )
        booking = bookings_factories.BookingFactory(
            stock=stock,
            status=BookingStatus.CONFIRMED,
            dateCreated=datetime.datetime.utcnow() + datetime.timedelta(hours=10),
        )

        response = self.make_request(plain_api_key, {"token": booking.token})

        assert response.status_code == 403
        assert response.json == {"booking": "This booking has not been used"}

    def test_should_raise_403_when_booking_has_activation_code(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        offer = offers_factories.DigitalOfferFactory(venue=venue_provider.venue)
        stock = offers_factories.StockWithActivationCodesFactory(offer=offer)
        booking = bookings_factories.UsedBookingFactory(stock=stock)
        offers_factories.ActivationCodeFactory(stock=booking.stock, booking=booking)

        response = self.make_request(plain_api_key, {"token": booking.token})

        assert response.status_code == 403
        assert response.json == {"booking": "This booking has validation codes, and cannot be marked as unused"}

    def test_should_raise_410_when_booking_is_cancelled(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        offer = offers_factories.ThingOfferFactory(venue=venue_provider.venue)
        stock = offers_factories.StockFactory(offer=offer)
        booking = bookings_factories.CancelledBookingFactory(stock=stock)

        response = self.make_request(plain_api_key, {"token": booking.token})

        assert response.status_code == 410
        assert response.json == {"booking": "This booking has been cancelled"}
