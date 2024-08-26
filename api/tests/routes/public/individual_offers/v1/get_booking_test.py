import datetime

from dateutil.relativedelta import relativedelta
import pytest

from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.finance import utils as finance_utils
from pcapi.core.offers import factories as offers_factories
from pcapi.utils import date as date_utils

from tests.conftest import TestClient
from tests.routes.public.helpers import PublicAPIVenueEndpointHelper


pytestmark = pytest.mark.usefixtures("db_session")


class GetBookingByTokenTest(PublicAPIVenueEndpointHelper):
    endpoint_url = "/public/bookings/v1/token/{token}"
    endpoint_method = "get"
    default_path_params = {"token": "TOKEN"}

    def setup_base_resource(self, venue=None):
        venue = venue or self.setup_venue()
        offer = offers_factories.ThingOfferFactory(
            venue=venue,
            description="Un livre de contrepèterie",
            name="Vieux motard que jamais",
            extraData={"ean": "1234567890123"},
        )
        past = datetime.datetime.utcnow() - datetime.timedelta(days=2)
        stock = offers_factories.StockFactory(offer=offer, beginningDatetime=past)
        booking = bookings_factories.BookingFactory(
            dateCreated=past - datetime.timedelta(days=2),
            user__email="beneficiary@example.com",
            user__phoneNumber="0101010101",
            user__dateOfBirth=datetime.datetime.utcnow() - relativedelta(years=18, months=2),
            user__postalCode="75001",
            stock=stock,
        )
        return offer, stock, booking

    def test_should_raise_404_because_has_no_access_to_venue(self, client: TestClient):
        plain_api_key, _ = self.setup_provider()
        _, _, booking = self.setup_base_resource()
        response = client.with_explicit_token(plain_api_key).get(self.endpoint_url.format(token=booking.token))
        assert response.status_code == 404

    def test_should_raise_404_because_venue_provider_is_inactive(self, client: TestClient):
        plain_api_key, venue_provider = self.setup_inactive_venue_provider()
        _, _, booking = self.setup_base_resource(venue=venue_provider.venue)
        response = client.with_explicit_token(plain_api_key).get(self.endpoint_url.format(token=booking.token))
        assert response.status_code == 404

    def test_should_raise_404_because_of_missing_token(self, client):
        response = client.get("/public/bookings/v1/token/")
        assert response.status_code == 404

    def test_key_has_rights_and_regular_product_offer(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        offer, stock, booking = self.setup_base_resource(venue=venue_provider.venue)

        response = client.with_explicit_token(plain_api_key).get(self.endpoint_url.format(token=booking.token))
        assert response.status_code == 200
        assert response.json == {
            "confirmationDate": date_utils.format_into_utc_date(booking.cancellationLimitDate),
            "creationDate": date_utils.format_into_utc_date(booking.dateCreated),
            "id": booking.id,
            "offerEan": "1234567890123",
            "offerId": offer.id,
            "offerName": offer.name,
            "price": finance_utils.to_eurocents(booking.amount),
            "status": "CONFIRMED",
            "priceCategoryId": None,
            "priceCategoryLabel": None,
            "quantity": booking.quantity,
            "stockId": stock.id,
            "userBirthDate": booking.user.birth_date.isoformat(),
            "userEmail": booking.user.email,
            "venueAddress": venue_provider.venue.street,
            "venueDepartementCode": venue_provider.venue.departementCode,
            "venueId": venue_provider.venue.id,
            "venueName": venue_provider.venue.name,
            "userFirstName": "Jeanne",
            "userLastName": "Doux",
            "userPhoneNumber": "+33101010101",
            "userPostalCode": "75001",
        }

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
            user__postalCode="69100",
            stock=event_stock,
        )

        response = client.with_explicit_token(plain_api_key).get(self.endpoint_url.format(token=booking.token))

        assert response.status_code == 200
        assert response.json == {
            "confirmationDate": date_utils.format_into_utc_date(booking.cancellationLimitDate),
            "creationDate": date_utils.format_into_utc_date(booking.dateCreated),
            "id": booking.id,
            "offerEan": None,
            "offerId": event_offer.id,
            "offerName": event_offer.name,
            "price": finance_utils.to_eurocents(booking.amount),
            "status": "CONFIRMED",
            "priceCategoryId": booking.stock.priceCategory.id,
            "priceCategoryLabel": booking.stock.priceCategory.label,
            "quantity": booking.quantity,
            "stockId": event_stock.id,
            "userBirthDate": booking.user.birth_date.isoformat(),
            "userEmail": booking.user.email,
            "venueAddress": venue_provider.venue.street,
            "venueDepartementCode": venue_provider.venue.departementCode,
            "venueId": venue_provider.venue.id,
            "venueName": venue_provider.venue.name,
            "userFirstName": "Jeanne",
            "userLastName": "Doux",
            "userPhoneNumber": "+33101010101",
            "userPostalCode": "69100",
        }

    def test_should_raise_403_when_booking_not_confirmed(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        next_week = datetime.datetime.utcnow() + datetime.timedelta(weeks=1)

        offer = offers_factories.ThingOfferFactory(venue=venue_provider.venue)
        stock = offers_factories.StockFactory(offer=offer, beginningDatetime=next_week)
        booking = bookings_factories.BookingFactory(stock=stock)

        response = client.with_explicit_token(plain_api_key).get(self.endpoint_url.format(token=booking.token))

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
        response = client.with_explicit_token(plain_api_key).get(self.endpoint_url.format(token=booking.token))

        # Then
        assert response.status_code == 403
        assert response.json == {"payment": "This booking has already been reimbursed"}

    def test_should_raise_410_when_booking_is_already_validated(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product_offer = offers_factories.ThingOfferFactory(venue=venue_provider.venue)
        product_stock = offers_factories.StockFactory(offer=product_offer)
        booking = bookings_factories.UsedBookingFactory(stock=product_stock)

        response = client.with_explicit_token(plain_api_key).get(self.endpoint_url.format(token=booking.token))

        assert response.status_code == 410
        assert response.json == {"booking": "This booking has already been validated"}

    def test_should_raise_410_when_booking_is_cancelled(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product_offer = offers_factories.ThingOfferFactory(venue=venue_provider.venue)
        product_stock = offers_factories.StockFactory(offer=product_offer)
        booking = bookings_factories.CancelledBookingFactory(stock=product_stock)

        response = client.with_explicit_token(plain_api_key).get(self.endpoint_url.format(token=booking.token))

        assert response.status_code == 410
        assert response.json == {"booking": "This booking has been cancelled"}
