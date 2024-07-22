import pytest

from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models
from pcapi.core.providers import factories as providers_factories

from . import utils


pytestmark = pytest.mark.usefixtures("db_session")


class PatchProviderTest:
    VENUE_PROVIDER_URL = "/public/providers/v1/venues"

    def test_should_update_notification_url(self, client):
        provider, _ = utils.create_offerer_provider(with_charlie=False)
        venue = offerers_factories.VenueFactory()
        venue_provider = providers_factories.VenueProviderFactory(provider=provider, venue=venue)
        venue_provider_external_urls = providers_factories.VenueProviderExternalUrlsFactory(
            venueProvider=venue_provider
        )
        previous_booking_url = venue_provider_external_urls.bookingExternalUrl
        previous_cancel_url = venue_provider_external_urls.cancelExternalUrl

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            f"{self.VENUE_PROVIDER_URL}/{venue.id}",
            json={"notificationUrl": "https://notifyMoi.baby"},
        )

        assert response.status_code == 204

        assert venue_provider_external_urls.notificationExternalUrl == "https://notifyMoi.baby"
        assert venue_provider_external_urls.bookingExternalUrl == previous_booking_url
        assert venue_provider_external_urls.cancelExternalUrl == previous_cancel_url

    def test_should_update_booking_url(self, client):
        provider, _ = utils.create_offerer_provider(with_charlie=False)
        venue = offerers_factories.VenueFactory()
        venue_provider = providers_factories.VenueProviderFactory(provider=provider, venue=venue)
        venue_provider_external_urls = providers_factories.VenueProviderExternalUrlsFactory(
            venueProvider=venue_provider
        )
        previous_cancel_url = venue_provider_external_urls.cancelExternalUrl
        previous_notification_url = venue_provider_external_urls.notificationExternalUrl

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            f"{self.VENUE_PROVIDER_URL}/{venue.id}",
            json={"bookingUrl": "https://bookmoi.baby"},
        )

        assert response.status_code == 204

        assert venue_provider_external_urls.notificationExternalUrl == previous_notification_url
        assert venue_provider_external_urls.bookingExternalUrl == "https://bookmoi.baby"
        assert venue_provider_external_urls.cancelExternalUrl == previous_cancel_url

    def test_should_update_cancel_url(self, client):
        provider, _ = utils.create_offerer_provider(with_charlie=False)
        venue = offerers_factories.VenueFactory()
        venue_provider = providers_factories.VenueProviderFactory(provider=provider, venue=venue)
        venue_provider_external_urls = providers_factories.VenueProviderExternalUrlsFactory(
            venueProvider=venue_provider
        )
        previous_booking_url = venue_provider_external_urls.bookingExternalUrl
        previous_notification_url = venue_provider_external_urls.notificationExternalUrl

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            f"{self.VENUE_PROVIDER_URL}/{venue.id}",
            json={"cancelUrl": "https://cancelmoi.baby"},
        )

        assert response.status_code == 204

        assert venue_provider_external_urls.notificationExternalUrl == previous_notification_url
        assert venue_provider_external_urls.bookingExternalUrl == previous_booking_url
        assert venue_provider_external_urls.cancelExternalUrl == "https://cancelmoi.baby"

    def test_should_delete_venue_provider_external_urls(self, client):
        provider, _ = utils.create_offerer_provider(with_charlie=False)
        venue = offerers_factories.VenueFactory()
        venue_provider = providers_factories.VenueProviderFactory(provider=provider, venue=venue)
        venue_provider_external_urls = providers_factories.VenueProviderExternalUrlsFactory(
            venueProvider=venue_provider
        )
        assert venue_provider.externalUrls == venue_provider_external_urls

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            f"{self.VENUE_PROVIDER_URL}/{venue.id}",
            json={"cancelUrl": None, "notificationUrl": None, "bookingUrl": None},
        )

        assert response.status_code == 204
        assert venue_provider.externalUrls == None

    def test_should_create_venue_provider_external_urls(self, client):
        provider, _ = utils.create_offerer_provider(with_charlie=False)
        venue = offerers_factories.VenueFactory()
        venue_provider = providers_factories.VenueProviderFactory(provider=provider, venue=venue)

        assert venue_provider.externalUrls == None

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            f"{self.VENUE_PROVIDER_URL}/{venue.id}",
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
    def test_should_raise_401_because_not_authenticated(self, client):
        venue = offerers_factories.VenueFactory()
        response = client.patch(
            f"{self.VENUE_PROVIDER_URL}/{venue.id}",
            json={
                "cancelUrl": "https://jemesaouleavec.le",
                "notificationUrl": "https://bru.it",
                "bookingUrl": "https://desge.ns",
            },
        )
        assert response.status_code == 401

    def test_should_raise_404_because_venue_does_not_exists(self, client):
        utils.create_offerer_provider(with_charlie=False)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            f"{self.VENUE_PROVIDER_URL}/123456789",
            json={"notificationUrl": "https://notifyMoi.baby"},
        )

        assert response.status_code == 404

    def test_should_raise_404_because_venue_not_linked_to_provider(self, client):
        utils.create_offerer_provider(with_charlie=False)
        venue = offerers_factories.VenueFactory()

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            f"{self.VENUE_PROVIDER_URL}/{venue.id}",
            json={"notificationUrl": "https://notifyMoi.baby"},
        )

        assert response.status_code == 404

    def test_should_raise_400_because_ticketing_urls_cannot_be_unset(self, client):
        provider_without_ticketing_urls, _ = utils.create_offerer_provider(with_charlie=False)
        venue = offerers_factories.VenueFactory()
        venue_provider = providers_factories.VenueProviderFactory(provider=provider_without_ticketing_urls, venue=venue)
        venue_provider_external_urls = providers_factories.VenueProviderExternalUrlsFactory(
            venueProvider=venue_provider
        )
        event_offer = offers_factories.EventOfferFactory(
            lastProvider=provider_without_ticketing_urls,
            venue=venue,
            withdrawalType=offers_models.WithdrawalTypeEnum.IN_APP,
        )
        offers_factories.StockFactory(offer=event_offer)
        previous_booking_url = venue_provider_external_urls.bookingExternalUrl
        previous_cancel_url = venue_provider_external_urls.cancelExternalUrl

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            f"{self.VENUE_PROVIDER_URL}/{venue.id}",
            json={"cancelUrl": None, "bookingUrl": None},
        )

        assert response.status_code == 400
        assert response.json == {
            "ticketing_urls": {
                "description": "You cannot unset your `booking_url` and `cancel_url` because you have event(s) with stocks linked to your ticketing system",
                "blocking_events_ids": [event_offer.id],
            }
        }

        assert venue_provider_external_urls.bookingExternalUrl == previous_booking_url
        assert venue_provider_external_urls.cancelExternalUrl == previous_cancel_url

    def test_should_raise_400_because_try_to_set_booking_url_only(self, client):
        provider_without_ticketing_urls, _ = utils.create_offerer_provider(with_charlie=False)
        venue = offerers_factories.VenueFactory()
        venue_provider = providers_factories.VenueProviderFactory(provider=provider_without_ticketing_urls, venue=venue)

        assert venue_provider.externalUrls == None

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            f"{self.VENUE_PROVIDER_URL}/{venue.id}",
            json={"bookingUrl": "https://coucou.com"},
        )

        assert response.status_code == 400
        assert response.json == {
            "ticketing_urls": "Your `booking_url` and `cancel_url` must be either both set or both unset"
        }

        assert venue_provider.externalUrls == None

    def test_should_raise_400_because_try_to_unset_only_cancel_url(self, client):
        provider_without_ticketing_urls, _ = utils.create_offerer_provider(with_charlie=False)
        venue = offerers_factories.VenueFactory()
        venue_provider = providers_factories.VenueProviderFactory(provider=provider_without_ticketing_urls, venue=venue)
        venue_provider_external_urls = providers_factories.VenueProviderExternalUrlsFactory(
            venueProvider=venue_provider
        )
        previous_booking_url = venue_provider_external_urls.bookingExternalUrl
        previous_cancel_url = venue_provider_external_urls.cancelExternalUrl

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            f"{self.VENUE_PROVIDER_URL}/{venue.id}",
            json={"cancelUrl": None},
        )

        assert response.status_code == 400
        assert response.json == {
            "ticketing_urls": "Your `booking_url` and `cancel_url` must be either both set or both unset"
        }
        assert venue_provider_external_urls.bookingExternalUrl == previous_booking_url
        assert venue_provider_external_urls.cancelExternalUrl == previous_cancel_url
