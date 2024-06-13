import decimal

import pytest

from pcapi.core import testing
from pcapi.core.categories import subcategories_v2 as subcategories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models
from pcapi.core.testing import assert_no_duplicated_queries

from . import utils


@pytest.mark.usefixtures("db_session")
class GetEventsTest:
    def test_get_first_page(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()
        offers = offers_factories.EventOfferFactory.create_batch(6, venue=venue)
        offers_factories.ThingOfferFactory.create_batch(3, venue=venue)  # not returned

        with testing.assert_no_duplicated_queries():
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
                f"/public/offers/v1/events?limit=5&venueId={venue.id}"
            )

        assert response.status_code == 200
        assert [event["id"] for event in response.json["events"]] == [offer.id for offer in offers[0:5]]

    # This test should be removed when our database has consistant data
    def test_get_offers_with_missing_fields(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()
        offer = offers_factories.EventOfferFactory(
            venue=venue,
            subcategoryId=subcategories.CONCERT.id,
            extraData={"musicType": "800"},
            bookingContact="nonValidEmail@email",
            bookingEmail="another@non.valid;email",
            externalTicketOfficeUrl="http:/invalidUrl.www",
        )
        offers_factories.PriceCategoryFactory(offer=offer, price=decimal.Decimal("400.12"))
        offers_factories.EventStockFactory(offer=offer, price=decimal.Decimal("400.12"))
        offers_factories.EventOfferFactory(
            venue=venue,
            subcategoryId=subcategories.CONCERT.id,
            withdrawalType=offers_models.WithdrawalTypeEnum.ON_SITE,
        )

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
            f"/public/offers/v1/events?limit=5&venueId={venue.id}"
        )

        assert response.status_code == 200
        assert len(response.json["events"]) == 2

    def test_get_events_without_sub_types(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()
        offers_factories.EventOfferFactory(
            subcategoryId=subcategories.CONCERT.id,
            venue=venue,
            extraData={"musicType": "800"},
        )
        offers_factories.EventOfferFactory(
            subcategoryId=subcategories.SPECTACLE_REPRESENTATION.id,
            venue=venue,
            extraData={"showType": "800"},
        )
        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
            f"/public/offers/v1/events?limit=5&venueId={venue.id}"
        )
        assert response.status_code == 200
        assert len(response.json["events"]) == 2

    def test_get_events_using_ids_at_provider(self, client):
        id_at_provider_1 = "unBelId"
        id_at_provider_2 = "unMagnifiqueId"
        id_at_provider_3 = "unIdCheumDeOuf"

        venue, _ = utils.create_offerer_provider_linked_to_venue()
        event_1 = offers_factories.EventOfferFactory(
            venue=venue,
            idAtProvider=id_at_provider_1,
        )
        event_2 = offers_factories.EventOfferFactory(
            venue=venue,
            idAtProvider=id_at_provider_2,
        )
        offers_factories.EventOfferFactory(
            venue=venue,
            idAtProvider=id_at_provider_3,
        )

        with assert_no_duplicated_queries():
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
                f"/public/offers/v1/events?limit=5&venueId={venue.id}&idsAtProvider={id_at_provider_1},{id_at_provider_2}"
            )

        assert response.status_code == 200
        assert [event["id"] for event in response.json["events"]] == [event_1.id, event_2.id]

    def test_404_when_venue_id_not_tied_to_api_key(self, client):
        utils.create_offerer_provider_linked_to_venue()
        unrelated_venue = offerers_factories.VenueFactory()

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
            f"/public/offers/v1/events?venueId={unrelated_venue.id}"
        )

        assert response.status_code == 404

    def test_404_when_inactive_venue_provider(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue(is_venue_provider_active=False)
        offers_factories.EventOfferFactory(venue=venue)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
            f"/public/offers/v1/events?limit=5&venueId={venue.id}"
        )

        assert response.status_code == 404
