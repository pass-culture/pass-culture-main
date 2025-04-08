import datetime

from dateutil.relativedelta import relativedelta
import pytest

from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.offers import factories as offers_factories

from tests.conftest import TestClient
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

    def test_should_raise_404_because_has_no_access_to_venue(self, client: TestClient):
        plain_api_key, _ = self.setup_provider()
        _, booking = self.setup_base_resource()
        response = client.with_explicit_token(plain_api_key).patch(self.endpoint_url.format(token=booking.token))
        assert response.status_code == 404

    def test_should_raise_404_because_venue_provider_is_inactive(self, client: TestClient):
        plain_api_key, venue_provider = self.setup_inactive_venue_provider()
        _, booking = self.setup_base_resource(venue=venue_provider.venue)
        response = client.with_explicit_token(plain_api_key).patch(self.endpoint_url.format(token=booking.token))
        assert response.status_code == 404

    def test_should_raise_404_because_of_missing_token(self, client):
        response = client.patch("/public/bookings/v1/cancel/token/")
        assert response.status_code == 404

    def test_key_has_rights_and_regular_product_offer(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        _, booking = self.setup_base_resource(venue=venue_provider.venue)

        response = client.with_explicit_token(plain_api_key).patch(self.endpoint_url.format(token=booking.token))

        assert response.status_code == 204
        assert booking.status is BookingStatus.CANCELLED

    def test_key_has_rights_and_regular_event_offer(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event_offer = offers_factories.EventOfferFactory(
            venue=venue_provider.venue,
            description="Un livre de contrepèterie",
            name="Vieux motard que jamais",
        )
        yesterday = datetime.datetime.utcnow() - datetime.timedelta(days=1)
        in_3_days = datetime.datetime.utcnow() + datetime.timedelta(days=3)
        event_stock = offers_factories.EventStockFactory(offer=event_offer, beginningDatetime=in_3_days)
        booking = bookings_factories.BookingFactory(
            dateCreated=yesterday,
            user__email="beneficiary@example.com",
            user__phoneNumber="0101010101",
            user__dateOfBirth=datetime.datetime.utcnow() - relativedelta(years=18, months=2),
            stock=event_stock,
        )

        response = client.with_explicit_token(plain_api_key).patch(self.endpoint_url.format(token=booking.token))

        assert response.status_code == 204
        assert booking.status == BookingStatus.CANCELLED

    def test_should_raise_403_when_booking_event_in_less_than_48_hours(self, client: TestClient):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        tomorrow = datetime.datetime.utcnow() + datetime.timedelta(days=1)

        offer = offers_factories.EventOfferFactory(venue=venue_provider.venue)
        stock = offers_factories.EventStockFactory(offer=offer, beginningDatetime=tomorrow)
        booking = bookings_factories.BookingFactory(stock=stock)

        response = client.with_explicit_token(plain_api_key).patch(self.endpoint_url.format(token=booking.token))

        assert response.json == {"booking": "This booking cannot be cancelled anymore"}
        assert response.status_code == 403

    def test_should_raise_403_when_cancelling_after_48_hours_following_booking_date(self, client: TestClient):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        in_2_weeks = datetime.datetime.utcnow() + datetime.timedelta(weeks=1)
        two_days_ago = datetime.datetime.utcnow() - datetime.timedelta(days=2)

        offer = offers_factories.EventOfferFactory(venue=venue_provider.venue)
        stock = offers_factories.EventStockFactory(offer=offer, beginningDatetime=in_2_weeks)
        booking = bookings_factories.BookingFactory(stock=stock, dateCreated=two_days_ago)

        response = client.with_explicit_token(plain_api_key).patch(self.endpoint_url.format(token=booking.token))

        assert response.json == {"booking": "This booking cannot be cancelled anymore"}
        assert response.status_code == 403

    def test_when_cancelling_less_than_48_hours_before_beginning_date(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        yesterday = datetime.datetime.utcnow() - datetime.timedelta(days=1)
        in_36_hours = datetime.datetime.utcnow() + datetime.timedelta(hours=36)

        offer = offers_factories.EventOfferFactory(venue=venue_provider.venue)
        stock = offers_factories.EventStockFactory(offer=offer, beginningDatetime=in_36_hours)
        booking = bookings_factories.BookingFactory(stock=stock, dateCreated=yesterday)

        response = client.with_explicit_token(plain_api_key).patch(self.endpoint_url.format(token=booking.token))

        assert response.json == {"booking": "This booking cannot be cancelled anymore"}
        assert response.status_code == 403

    def test_should_raise_403_when_booking_is_refunded(self, client):
        # Given
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        offer = offers_factories.ThingOfferFactory(venue=venue_provider.venue)
        stock = offers_factories.StockFactory(offer=offer)
        booking = bookings_factories.ReimbursedBookingFactory(stock=stock)

        # When
        response = client.with_explicit_token(plain_api_key).patch(self.endpoint_url.format(token=booking.token))

        # Then
        assert response.status_code == 403
        assert response.json == {"payment": "This booking has been reimbursed"}

    def test_should_raise_410_when_booking_is_already_cancelled(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product_offer = offers_factories.ThingOfferFactory(venue=venue_provider.venue)
        product_stock = offers_factories.StockFactory(offer=product_offer)
        booking = bookings_factories.CancelledBookingFactory(stock=product_stock)

        response = client.with_explicit_token(plain_api_key).patch(self.endpoint_url.format(token=booking.token))

        assert response.status_code == 410
        assert response.json == {"booking": "This booking has already been cancelled"}

    def test_should_raise_410_when_booking_is_used(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product_offer = offers_factories.ThingOfferFactory(venue=venue_provider.venue)
        product_stock = offers_factories.StockFactory(offer=product_offer)
        booking = bookings_factories.UsedBookingFactory(stock=product_stock)

        response = client.with_explicit_token(plain_api_key).patch(self.endpoint_url.format(token=booking.token))

        assert response.status_code == 410
        assert response.json == {"booking": "This booking has been validated"}
