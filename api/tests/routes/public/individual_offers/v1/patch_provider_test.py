import pytest

from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models
from pcapi.core.providers import factories as providers_factories

from tests.routes.public.helpers import PublicAPIEndpointBaseHelper


pytestmark = pytest.mark.usefixtures("db_session")


class PatchProviderTest(PublicAPIEndpointBaseHelper):
    endpoint_url = "/public/providers/v1/provider"

    def test_should_raise_401_because_not_authenticated(self, client):
        response = client.patch(self.endpoint_url, json={})
        assert response.status_code == 401

    def test_should_update_notification_url(self, client):
        plain_api_key, provider = self.setup_provider()
        previous_booking_url = provider.bookingExternalUrl
        previous_cancel_url = provider.cancelExternalUrl

        response = client.with_explicit_token(plain_api_key).patch(
            self.endpoint_url, json={"notificationUrl": "https://notifyMoi.baby"}
        )

        assert response.status_code == 200
        assert response.json == {
            "id": provider.id,
            "name": provider.name,
            "logoUrl": provider.logoUrl,
            "notificationUrl": "https://notifyMoi.baby",
            "bookingUrl": previous_booking_url,
            "cancelUrl": previous_cancel_url,
        }

        assert provider.notificationExternalUrl == "https://notifyMoi.baby"
        assert provider.bookingExternalUrl == previous_booking_url
        assert provider.cancelExternalUrl == previous_cancel_url

    def test_should_update_booking_url(self, client):
        plain_api_key, provider = self.setup_provider()
        previous_cancel_url = provider.cancelExternalUrl
        previous_notification_url = provider.notificationExternalUrl

        response = client.with_explicit_token(plain_api_key).patch(
            self.endpoint_url, json={"bookingUrl": "https://ohouibook.moi"}
        )

        assert response.status_code == 200
        assert response.json == {
            "id": provider.id,
            "name": provider.name,
            "logoUrl": provider.logoUrl,
            "notificationUrl": previous_notification_url,
            "bookingUrl": "https://ohouibook.moi",
            "cancelUrl": previous_cancel_url,
        }

        assert provider.notificationExternalUrl == previous_notification_url
        assert provider.bookingExternalUrl == "https://ohouibook.moi"
        assert provider.cancelExternalUrl == previous_cancel_url

    def test_should_update_cancel_url(self, client):
        plain_api_key, provider = self.setup_provider()
        previous_booking_url = provider.bookingExternalUrl
        previous_notification_url = provider.notificationExternalUrl

        response = client.with_explicit_token(plain_api_key).patch(
            self.endpoint_url, json={"cancelUrl": "https://ohnoncancel.moi/pas"}
        )

        assert response.status_code == 200
        assert response.json == {
            "id": provider.id,
            "name": provider.name,
            "logoUrl": provider.logoUrl,
            "notificationUrl": previous_notification_url,
            "bookingUrl": previous_booking_url,
            "cancelUrl": "https://ohnoncancel.moi/pas",
        }

        assert provider.notificationExternalUrl == previous_notification_url
        assert provider.bookingExternalUrl == previous_booking_url
        assert provider.cancelExternalUrl == "https://ohnoncancel.moi/pas"

    def test_should_unset_ticketing_urls(self, client):
        plain_api_key, provider = self.setup_provider()
        previous_notification_url = provider.notificationExternalUrl

        response = client.with_explicit_token(plain_api_key).patch(
            self.endpoint_url, json={"cancelUrl": None, "bookingUrl": None}
        )

        assert response.status_code == 200
        assert response.json == {
            "id": provider.id,
            "name": provider.name,
            "logoUrl": provider.logoUrl,
            "notificationUrl": previous_notification_url,
            "bookingUrl": None,
            "cancelUrl": None,
        }

        assert provider.notificationExternalUrl == previous_notification_url
        assert provider.bookingExternalUrl == None
        assert provider.cancelExternalUrl == None

    def test_should_return_400_because_it_is_not_possible_to_unset_ticketing_urls(self, client):
        plain_api_key, provider = self.setup_provider()
        previous_booking_url = provider.bookingExternalUrl
        previous_cancel_url = provider.cancelExternalUrl
        previous_notification_url = provider.notificationExternalUrl
        venue = offerers_factories.VenueFactory()
        providers_factories.VenueProviderFactory(provider=provider, venue=venue)
        event_offer = offers_factories.EventOfferFactory(
            lastProvider=provider, venue=venue, withdrawalType=offers_models.WithdrawalTypeEnum.IN_APP
        )
        offers_factories.StockFactory(offer=event_offer)

        response = client.with_explicit_token(plain_api_key).patch(
            self.endpoint_url, json={"cancelUrl": None, "bookingUrl": None}
        )

        assert response.status_code == 400
        assert response.json == {
            "ticketing_urls": {
                "description": "You cannot unset your `booking_url` and `cancel_url` because you have event(s) with stocks linked to your ticketing system",
                "blocking_events_ids": [event_offer.id],
            }
        }

        assert provider.notificationExternalUrl == previous_notification_url
        assert provider.bookingExternalUrl == previous_booking_url
        assert provider.cancelExternalUrl == previous_cancel_url

    def test_should_return_400_because_of_incoherent_ticketing_urls(self, client):
        plain_api_key, provider = self.setup_provider()
        previous_booking_url = provider.bookingExternalUrl
        previous_cancel_url = provider.cancelExternalUrl
        previous_notification_url = provider.notificationExternalUrl

        response = client.with_explicit_token(plain_api_key).patch(self.endpoint_url, json={"cancelUrl": None})

        assert response.status_code == 400
        assert response.json == {
            "ticketing_urls": "Your `booking_url` and `cancel_url` must be either both set or both unset"
        }

        assert provider.notificationExternalUrl == previous_notification_url
        assert provider.bookingExternalUrl == previous_booking_url
        assert provider.cancelExternalUrl == previous_cancel_url
