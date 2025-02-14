import pytest

from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models
from pcapi.core.providers import factories as providers_factories

from tests.conftest import TestClient
from tests.routes.public.helpers import PublicAPIVenueEndpointHelper


pytestmark = pytest.mark.usefixtures("db_session")


class PatchVenueProviderExternalUrlsTest(PublicAPIVenueEndpointHelper):
    endpoint_url = "/public/providers/v1/venues/{venue_id}"
    endpoint_method = "patch"
    default_path_params = {"venue_id": 1}

    def test_should_raise_401_because_api_key_is_not_linked_to_provider(self, client: TestClient):
        old_api_key = self.setup_old_api_key()
        venue = self.setup_venue()
        response = client.with_explicit_token(old_api_key).patch(self.endpoint_url.format(venue_id=venue.id))
        assert response.status_code == 401
        assert response.json == {"auth": "Deprecated API key. Please contact provider support to get a new API key"}

    def test_should_raise_404_because_venue_provider_is_inactive(self, client: TestClient):
        plain_api_key, venue_provider = self.setup_inactive_venue_provider()
        response = client.with_explicit_token(plain_api_key).patch(
            self.endpoint_url.format(venue_id=venue_provider.venue.id)
        )
        assert response.status_code == 404

    def test_should_raise_404_because_has_no_access_to_venue(self, client: TestClient):
        plain_api_key, _ = self.setup_provider()
        venue = self.setup_venue()
        response = client.with_explicit_token(plain_api_key).patch(self.endpoint_url.format(venue_id=venue.id))
        assert response.status_code == 404

    def test_should_update_notification_url(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        venue_provider_external_urls = providers_factories.VenueProviderExternalUrlsFactory(
            venueProvider=venue_provider
        )
        previous_booking_url = venue_provider_external_urls.bookingExternalUrl
        previous_cancel_url = venue_provider_external_urls.cancelExternalUrl

        response = client.with_explicit_token(plain_api_key).patch(
            self.endpoint_url.format(venue_id=venue_provider.venue.id),
            json={"notificationUrl": "https://notifyMoi.baby"},
        )

        assert response.status_code == 204

        assert venue_provider_external_urls.notificationExternalUrl == "https://notifyMoi.baby"
        assert venue_provider_external_urls.bookingExternalUrl == previous_booking_url
        assert venue_provider_external_urls.cancelExternalUrl == previous_cancel_url

    def test_should_update_booking_url(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        venue_provider_external_urls = providers_factories.VenueProviderExternalUrlsFactory(
            venueProvider=venue_provider
        )
        previous_cancel_url = venue_provider_external_urls.cancelExternalUrl
        previous_notification_url = venue_provider_external_urls.notificationExternalUrl

        response = client.with_explicit_token(plain_api_key).patch(
            self.endpoint_url.format(venue_id=venue_provider.venue.id),
            json={"bookingUrl": "https://bookmoi.baby"},
        )

        assert response.status_code == 204

        assert venue_provider_external_urls.notificationExternalUrl == previous_notification_url
        assert venue_provider_external_urls.bookingExternalUrl == "https://bookmoi.baby"
        assert venue_provider_external_urls.cancelExternalUrl == previous_cancel_url

    def test_should_update_cancel_url(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        venue_provider_external_urls = providers_factories.VenueProviderExternalUrlsFactory(
            venueProvider=venue_provider
        )
        previous_booking_url = venue_provider_external_urls.bookingExternalUrl
        previous_notification_url = venue_provider_external_urls.notificationExternalUrl

        response = client.with_explicit_token(plain_api_key).patch(
            self.endpoint_url.format(venue_id=venue_provider.venue.id),
            json={"cancelUrl": "https://cancelmoi.baby"},
        )

        assert response.status_code == 204

        assert venue_provider_external_urls.notificationExternalUrl == previous_notification_url
        assert venue_provider_external_urls.bookingExternalUrl == previous_booking_url
        assert venue_provider_external_urls.cancelExternalUrl == "https://cancelmoi.baby"

    def test_should_delete_venue_provider_external_urls(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        venue_provider_external_urls = providers_factories.VenueProviderExternalUrlsFactory(
            venueProvider=venue_provider
        )
        assert venue_provider.externalUrls == venue_provider_external_urls

        response = client.with_explicit_token(plain_api_key).patch(
            self.endpoint_url.format(venue_id=venue_provider.venue.id),
            json={"cancelUrl": None, "notificationUrl": None, "bookingUrl": None},
        )

        assert response.status_code == 204
        assert venue_provider.externalUrls == None

    def test_should_create_venue_provider_external_urls(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()

        assert venue_provider.externalUrls == None

        response = client.with_explicit_token(plain_api_key).patch(
            self.endpoint_url.format(venue_id=venue_provider.venue.id),
            json={
                "cancelUrl": "https://jemesaouleavec.le",
                "notificationUrl": "https://bru.it",
                "bookingUrl": "https://desge.ns",
            },
        )

        assert response.status_code == 204
        assert venue_provider.externalUrls.cancelExternalUrl == "https://jemesaouleavec.le"
        assert venue_provider.externalUrls.notificationExternalUrl == "https://bru.it"
        assert venue_provider.externalUrls.bookingExternalUrl == "https://desge.ns"

    # Error
    def test_should_raise_404_because_venue_does_not_exists(self, client):
        plain_api_key, _ = self.setup_provider()

        response = client.with_explicit_token(plain_api_key).patch(
            self.endpoint_url.format(venue_id="123456789"),
            json={"notificationUrl": "https://notifyMoi.baby"},
        )

        assert response.status_code == 404

    def test_should_raise_400_because_ticketing_urls_cannot_be_unset(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider(provider_has_ticketing_urls=False)

        venue_provider_external_urls = providers_factories.VenueProviderExternalUrlsFactory(
            venueProvider=venue_provider
        )
        event_offer = offers_factories.EventOfferFactory(
            lastProvider=venue_provider.provider,
            venue=venue_provider.venue,
            withdrawalType=offers_models.WithdrawalTypeEnum.IN_APP,
        )
        offers_factories.StockFactory(offer=event_offer)
        previous_booking_url = venue_provider_external_urls.bookingExternalUrl
        previous_cancel_url = venue_provider_external_urls.cancelExternalUrl

        response = client.with_explicit_token(plain_api_key).patch(
            self.endpoint_url.format(venue_id=venue_provider.venue.id),
            json={"cancelUrl": None, "bookingUrl": None},
        )

        assert response.status_code == 400
        assert response.json == {
            "ticketing_urls": [
                f"You cannot unset your `booking_url` and `cancel_url` because you have event(s) with stocks linked to your ticketing system. Blocking event ids: {[event_offer.id]}",
            ]
        }

        assert venue_provider_external_urls.bookingExternalUrl == previous_booking_url
        assert venue_provider_external_urls.cancelExternalUrl == previous_cancel_url

    def test_should_raise_400_because_try_to_set_booking_url_only(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider(provider_has_ticketing_urls=False)

        assert venue_provider.externalUrls == None

        response = client.with_explicit_token(plain_api_key).patch(
            self.endpoint_url.format(venue_id=venue_provider.venue.id),
            json={"bookingUrl": "https://coucou.com"},
        )

        assert response.status_code == 400
        assert response.json == {
            "ticketing_urls": ["Your `booking_url` and `cancel_url` must be either both set or both unset"]
        }

        assert venue_provider.externalUrls == None

    def test_should_raise_400_because_try_to_unset_only_cancel_url(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider(provider_has_ticketing_urls=False)
        venue_provider_external_urls = providers_factories.VenueProviderExternalUrlsFactory(
            venueProvider=venue_provider
        )
        previous_booking_url = venue_provider_external_urls.bookingExternalUrl
        previous_cancel_url = venue_provider_external_urls.cancelExternalUrl

        response = client.with_explicit_token(plain_api_key).patch(
            self.endpoint_url.format(venue_id=venue_provider.venue.id),
            json={"cancelUrl": None},
        )

        assert response.status_code == 400
        assert response.json == {
            "ticketing_urls": ["Your `booking_url` and `cancel_url` must be either both set or both unset"]
        }
        assert venue_provider_external_urls.bookingExternalUrl == previous_booking_url
        assert venue_provider_external_urls.cancelExternalUrl == previous_cancel_url
