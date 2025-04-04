import datetime

from dateutil.relativedelta import relativedelta
import pytest

from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.bookings import models as bookings_models
from pcapi.core.categories import subcategories
from pcapi.core.offers import factories as offers_factories
from pcapi.models import db
from pcapi.models.validation_status_mixin import ValidationStatus
from pcapi.utils import date as date_utils

from tests.conftest import TestClient
from tests.routes.public.helpers import PublicAPIVenueEndpointHelper


pytestmark = pytest.mark.usefixtures("db_session")


class ValidateBookingByTokenTest(PublicAPIVenueEndpointHelper):
    endpoint_url = "/public/bookings/v1/use/token/{token}"
    endpoint_method = "patch"
    default_path_params = {"token": "TOKEN"}

    def setup_base_resource(self, venue=None):
        venue = venue or self.setup_venue()
        offer = offers_factories.ThingOfferFactory(
            subcategoryId=subcategories.LIVRE_PAPIER.id,
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

    def test_key_has_rights_and_regular_product_offer(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        _, booking = self.setup_base_resource(venue=venue_provider.venue)

        response = client.with_explicit_token(plain_api_key).patch(self.endpoint_url.format(token=booking.token))

        assert response.status_code == 204
        assert booking.is_used_or_reimbursed is True
        assert booking.user.achievements

    def test_key_has_rights_and_regular_event_offer(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event_offer = offers_factories.EventOfferFactory(
            venue=venue_provider.venue,
            description="Un livre de contrepèterie",
            name="Vieux motard que jamais",
        )
        past = datetime.datetime.utcnow() - datetime.timedelta(days=2)
        event_stock = offers_factories.EventStockFactory(offer=event_offer, beginningDatetime=past)
        booking = bookings_factories.BookingFactory(
            dateCreated=past - datetime.timedelta(days=2),
            user__email="beneficiary@example.com",
            user__phoneNumber="0101010101",
            user__dateOfBirth=datetime.datetime.utcnow() - relativedelta(years=18, months=2),
            stock=event_stock,
        )

        response = client.with_explicit_token(plain_api_key).patch(self.endpoint_url.format(token=booking.token))

        assert response.status_code == 204
        assert booking.is_used_or_reimbursed is True
        assert booking.user.achievements

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
        response = client.patch(self.endpoint_url.format(token=""))
        assert response.status_code == 404

    def test_should_raise_403_when_booking_not_confirmed(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        next_week = datetime.datetime.utcnow() + datetime.timedelta(weeks=1)

        offer = offers_factories.ThingOfferFactory(venue=venue_provider.venue)
        stock = offers_factories.StockFactory(offer=offer, beginningDatetime=next_week)
        booking = bookings_factories.BookingFactory(stock=stock)

        response = client.with_explicit_token(plain_api_key).patch(self.endpoint_url.format(token=booking.token))

        cancellation_limit_date = datetime.datetime.strftime(
            date_utils.utc_datetime_to_department_timezone(
                booking.cancellationLimitDate, booking.venue.departementCode
            ),
            "%d/%m/%Y à %H:%M",
        )

        assert response.json == {
            "booking": f"Vous pourrez valider cette contremarque à partir du {cancellation_limit_date}, une fois le délai d’annulation passé."
        }
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
        assert response.json == {"payment": "This booking has already been reimbursed"}

    def test_should_raise_403_when_offerer_is_closed(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()

        offerer = venue_provider.venue.managingOfferer
        offerer.validationStatus = ValidationStatus.CLOSED
        db.session.add(offerer)
        db.session.flush()

        offer = offers_factories.ThingOfferFactory(venue=venue_provider.venue)
        stock = offers_factories.StockFactory(offer=offer)
        booking = bookings_factories.BookingFactory(stock=stock)

        response = client.with_explicit_token(plain_api_key).patch(self.endpoint_url.format(token=booking.token))
        assert response.status_code == 403
        assert response.json == {"booking": ["Vous ne pouvez plus valider de contremarque sur une structure fermée"]}
        assert booking.status == bookings_models.BookingStatus.CONFIRMED

    def test_should_raise_410_when_booking_is_already_validated(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product_offer = offers_factories.ThingOfferFactory(venue=venue_provider.venue)
        product_stock = offers_factories.StockFactory(offer=product_offer)
        booking = bookings_factories.UsedBookingFactory(stock=product_stock)

        response = client.with_explicit_token(plain_api_key).patch(self.endpoint_url.format(token=booking.token))

        assert response.status_code == 410
        assert response.json == {"booking": "This booking has already been validated"}

    def test_should_raise_410_when_booking_is_cancelled(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product_offer = offers_factories.ThingOfferFactory(venue=venue_provider.venue)
        product_stock = offers_factories.StockFactory(offer=product_offer)
        booking = bookings_factories.CancelledBookingFactory(stock=product_stock)

        response = client.with_explicit_token(plain_api_key).patch(self.endpoint_url.format(token=booking.token))

        assert response.status_code == 410
        assert response.json == {"booking": "This booking has been cancelled"}
