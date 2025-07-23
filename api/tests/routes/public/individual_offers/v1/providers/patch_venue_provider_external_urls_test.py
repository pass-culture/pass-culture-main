import pytest

from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models
from pcapi.core.providers import factories as providers_factories

from tests.routes.public.helpers import PublicAPIVenueEndpointHelper


pytestmark = pytest.mark.usefixtures("db_session")


class PatchVenueProviderExternalUrlsTest(PublicAPIVenueEndpointHelper):
    endpoint_url = "/public/providers/v1/venues/{venue_id}"
    endpoint_method = "patch"
    default_path_params = {"venue_id": 1}

    def test_should_raise_404_because_venue_provider_is_inactive(self):
        plain_api_key, venue_provider = self.setup_inactive_venue_provider()
        response = self.make_request(plain_api_key, {"venue_id": venue_provider.venue.id})
        assert response.status_code == 404

    def test_should_raise_404_because_has_no_access_to_venue(self):
        plain_api_key, _ = self.setup_provider()
        venue = self.setup_venue()
        response = self.make_request(plain_api_key, {"venue_id": venue.id})
        assert response.status_code == 404

    def test_should_update_notification_url(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        venue_provider_external_urls = providers_factories.VenueProviderExternalUrlsFactory(
            venueProvider=venue_provider
        )
        previous_booking_url = venue_provider_external_urls.bookingExternalUrl
        previous_cancel_url = venue_provider_external_urls.cancelExternalUrl

        response = self.make_request(
            plain_api_key,
            {"venue_id": venue_provider.venue.id},
            json_body={"notificationUrl": "https://notifyMoi.baby"},
        )

        assert response.status_code == 204

        assert venue_provider_external_urls.notificationExternalUrl == "https://notifyMoi.baby"
        assert venue_provider_external_urls.bookingExternalUrl == previous_booking_url
        assert venue_provider_external_urls.cancelExternalUrl == previous_cancel_url

    def test_should_update_booking_url(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        venue_provider_external_urls = providers_factories.VenueProviderExternalUrlsFactory(
            venueProvider=venue_provider
        )
        previous_cancel_url = venue_provider_external_urls.cancelExternalUrl
        previous_notification_url = venue_provider_external_urls.notificationExternalUrl

        response = self.make_request(
            plain_api_key,
            {"venue_id": venue_provider.venue.id},
            json_body={"bookingUrl": "https://bookmoi.baby"},
        )
        assert response.status_code == 204

        assert venue_provider_external_urls.notificationExternalUrl == previous_notification_url
        assert venue_provider_external_urls.bookingExternalUrl == "https://bookmoi.baby"
        assert venue_provider_external_urls.cancelExternalUrl == previous_cancel_url

    def test_should_update_cancel_url(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        venue_provider_external_urls = providers_factories.VenueProviderExternalUrlsFactory(
            venueProvider=venue_provider
        )
        previous_booking_url = venue_provider_external_urls.bookingExternalUrl
        previous_notification_url = venue_provider_external_urls.notificationExternalUrl

        response = self.make_request(
            plain_api_key,
            {"venue_id": venue_provider.venue.id},
            json_body={"cancelUrl": "https://cancelmoi.baby"},
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

        response = self.make_request(
            plain_api_key,
            {"venue_id": venue_provider.venue.id},
            json_body={"cancelUrl": None, "notificationUrl": None, "bookingUrl": None},
        )
        assert response.status_code == 204
        assert venue_provider.externalUrls == None

    def test_should_create_venue_provider_external_urls(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()

        assert venue_provider.externalUrls == None

        response = self.make_request(
            plain_api_key,
            {"venue_id": venue_provider.venue.id},
            json_body={
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
    def test_should_raise_404_because_venue_does_not_exists(self):
        plain_api_key, _ = self.setup_provider()

        response = self.make_request(plain_api_key, {"venue_id": "123456789"}, json_body={})

        assert response.status_code == 404

    def test_should_raise_400_because_ticketing_urls_cannot_be_unset(self):
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

        response = self.make_request(
            plain_api_key,
            {"venue_id": venue_provider.venue.id},
            json_body={"cancelUrl": None, "bookingUrl": None},
        )

        assert response.status_code == 400
        assert response.json == {
            "ticketing_urls": [
                f"You cannot unset your `booking_url` and `cancel_url` because you have event(s) with stocks linked to your ticketing system. Blocking event ids: {[event_offer.id]}",
            ]
        }

        assert venue_provider_external_urls.bookingExternalUrl == previous_booking_url
        assert venue_provider_external_urls.cancelExternalUrl == previous_cancel_url

    @pytest.mark.parametrize("payload", [{"cancelUrl": "https://coucou.com"}, {"bookingUrl": "https://coucou.com"}])
    def test_should_raise_400_because_try_to_set_only_one_ticketing_url(self, payload):
        plain_api_key, venue_provider = self.setup_active_venue_provider(provider_has_ticketing_urls=False)

        assert venue_provider.externalUrls == None

        response = self.make_request(plain_api_key, {"venue_id": venue_provider.venue.id}, json_body=payload)

        assert response.status_code == 400
        assert response.json == {
            "ticketing_urls": ["Your `booking_url` and `cancel_url` must be either both set or both unset"]
        }

        assert venue_provider.externalUrls == None

    @pytest.mark.parametrize("payload", [{"cancelUrl": None}, {"bookingUrl": None}])
    def test_should_raise_400_because_try_to_unset_only_one_ticketing_url(self, payload):
        plain_api_key, venue_provider = self.setup_active_venue_provider(provider_has_ticketing_urls=False)
        venue_provider_external_urls = providers_factories.VenueProviderExternalUrlsFactory(
            venueProvider=venue_provider
        )
        previous_booking_url = venue_provider_external_urls.bookingExternalUrl
        previous_cancel_url = venue_provider_external_urls.cancelExternalUrl

        response = self.make_request(plain_api_key, {"venue_id": venue_provider.venue.id}, json_body=payload)

        assert response.status_code == 400
        assert response.json == {
            "ticketing_urls": ["Your `booking_url` and `cancel_url` must be either both set or both unset"]
        }
        assert venue_provider_external_urls.bookingExternalUrl == previous_booking_url
        assert venue_provider_external_urls.cancelExternalUrl == previous_cancel_url
