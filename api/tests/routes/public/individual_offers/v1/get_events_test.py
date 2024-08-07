import decimal

import pytest

from pcapi.core import testing
from pcapi.core.categories import subcategories_v2 as subcategories
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models
from pcapi.core.testing import assert_no_duplicated_queries

from tests.routes.public.helpers import PublicAPIVenueEndpointHelper


@pytest.mark.usefixtures("db_session")
class GetEventsTest(PublicAPIVenueEndpointHelper):
    endpoint_url = "/public/offers/v1/events"

    def test_should_raise_401_because_not_authenticated(self, client):
        response = client.get(self.endpoint_url)
        assert response.status_code == 401

    def test_should_raise_404_because_has_no_access_to_venue(self, client):
        plain_api_key, _ = self.setup_provider()
        venue = self.setup_venue()
        response = client.with_explicit_token(plain_api_key).get("%s?venueId=%s" % (self.endpoint_url, venue.id))
        assert response.status_code == 404

    def test_should_raise_404_because_venue_provider_is_inactive(self, client):
        plain_api_key, venue_provider = self.setup_inactive_venue_provider()
        response = client.with_explicit_token(plain_api_key).get(
            self.endpoint_url, params={"venueId": venue_provider.venueId}
        )
        assert response.status_code == 404

    def test_get_first_page_old_behavior_when_permission_system_not_enforced(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        offers = offers_factories.EventOfferFactory.create_batch(6, venue=venue_provider.venue)
        offers_factories.ThingOfferFactory.create_batch(3, venue=venue_provider.venue)  # not returned

        with testing.assert_no_duplicated_queries():
            response = client.with_explicit_token(plain_api_key).get(
                self.endpoint_url, params={"venueId": venue_provider.venueId, "limit": 5}
            )

        assert response.status_code == 200
        assert [event["id"] for event in response.json["events"]] == [offer.id for offer in offers[0:5]]

    def test_get_first_page(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        offers = offers_factories.EventOfferFactory.create_batch(6, venue=venue_provider.venue)
        offers_factories.ThingOfferFactory.create_batch(3, venue=venue_provider.venue)  # not returned

        with testing.assert_no_duplicated_queries():
            response = client.with_explicit_token(plain_api_key).get(
                self.endpoint_url, params={"venueId": venue_provider.venueId, "limit": 5}
            )

        assert response.status_code == 200
        assert [event["id"] for event in response.json["events"]] == [offer.id for offer in offers[0:5]]

    # This test should be removed when our database has consistant data
    def test_get_offers_with_missing_fields(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        offer = offers_factories.EventOfferFactory(
            venue=venue_provider.venue,
            subcategoryId=subcategories.CONCERT.id,
            extraData={"musicType": "800"},
            bookingContact="nonValidEmail@email",
            bookingEmail="another@non.valid;email",
            externalTicketOfficeUrl="http:/invalidUrl.www",
        )
        offers_factories.PriceCategoryFactory(offer=offer, price=decimal.Decimal("400.12"))
        offers_factories.EventStockFactory(offer=offer, price=decimal.Decimal("400.12"))
        offers_factories.EventOfferFactory(
            venue=venue_provider.venue,
            subcategoryId=subcategories.CONCERT.id,
            withdrawalType=offers_models.WithdrawalTypeEnum.ON_SITE,
        )

        response = client.with_explicit_token(plain_api_key).get(
            self.endpoint_url, params={"venueId": venue_provider.venueId, "limit": 5}
        )

        assert response.status_code == 200
        assert len(response.json["events"]) == 2

    def test_get_events_without_sub_types(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        offers_factories.EventOfferFactory(
            subcategoryId=subcategories.CONCERT.id,
            venue=venue_provider.venue,
            extraData={"musicType": "800"},
        )
        offers_factories.EventOfferFactory(
            subcategoryId=subcategories.SPECTACLE_REPRESENTATION.id,
            venue=venue_provider.venue,
            extraData={"showType": "800"},
        )
        response = client.with_explicit_token(plain_api_key).get(
            self.endpoint_url, params={"venueId": venue_provider.venueId, "limit": 5}
        )
        assert response.status_code == 200
        assert len(response.json["events"]) == 2

    def test_get_events_using_ids_at_provider(self, client):
        id_at_provider_1 = "unBelId"
        id_at_provider_2 = "unMagnifiqueId"
        id_at_provider_3 = "unIdCheumDeOuf"

        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event_1 = offers_factories.EventOfferFactory(
            venue=venue_provider.venue,
            idAtProvider=id_at_provider_1,
        )
        event_2 = offers_factories.EventOfferFactory(
            venue=venue_provider.venue,
            idAtProvider=id_at_provider_2,
        )
        offers_factories.EventOfferFactory(
            venue=venue_provider.venue,
            idAtProvider=id_at_provider_3,
        )

        with assert_no_duplicated_queries():
            response = client.with_explicit_token(plain_api_key).get(
                self.endpoint_url,
                params={
                    "venueId": venue_provider.venueId,
                    "limit": 5,
                    "idsAtProvider": f"{id_at_provider_1},{id_at_provider_2}",
                },
            )

        assert response.status_code == 200
        assert [event["id"] for event in response.json["events"]] == [event_1.id, event_2.id]
