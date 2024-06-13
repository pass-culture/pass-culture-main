import pytest

from pcapi.core import testing
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers import factories as offers_factories

from . import utils


@pytest.mark.usefixtures("db_session")
class GetProductsTest:
    ENDPOINT_URL = "http://localhost/public/offers/v1/products"

    def test_get_first_page(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()
        offers = offers_factories.ThingOfferFactory.create_batch(12, venue=venue)

        with testing.assert_no_duplicated_queries():
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
                f"/public/offers/v1/products?venueId={venue.id}&limit=5"
            )

        assert response.status_code == 200
        assert [product["id"] for product in response.json["products"]] == [offer.id for offer in offers[0:5]]

    def test_get_last_page(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()
        offers = offers_factories.ThingOfferFactory.create_batch(12, venue=venue)

        with testing.assert_no_duplicated_queries():
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
                f"/public/offers/v1/products?venueId={venue.id}&limit=5&firstIndex={int(offers[10].id)}"
            )

        assert response.status_code == 200
        assert [product["id"] for product in response.json["products"]] == [offer.id for offer in offers[10:12]]

    def test_get_product_using_ids_at_provider(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()
        id_at_provider_1 = "une"
        id_at_provider_2 = "belle"
        id_at_provider_3 = "têteDeVainqueur"

        offer_1 = offers_factories.OfferFactory(idAtProvider=id_at_provider_1, venue=venue)
        offer_2 = offers_factories.OfferFactory(idAtProvider=id_at_provider_2, venue=venue)
        offers_factories.OfferFactory(idAtProvider=id_at_provider_3, venue=venue)

        with testing.assert_no_duplicated_queries():
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
                f"/public/offers/v1/products?venueId={venue.id}&limit=5&idsAtProvider={id_at_provider_1},{id_at_provider_2}"
            )

        assert response.status_code == 200
        assert [product["id"] for product in response.json["products"]] == [offer_1.id, offer_2.id]

    def test_should_return_a_200_event_if_the_offer_name_is_longer_than_90_signs_long(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()
        name_more_than_90_signs_long = (
            "Bébé, apprends-moi à devenir ton parent : naissance, sommeil, attachement, pleurs, développement"
        )
        offers_factories.ThingOfferFactory(venue=venue, name=name_more_than_90_signs_long)

        with testing.assert_no_duplicated_queries():
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
                f"/public/offers/v1/products?venueId={venue.id}"
            )

        assert response.status_code == 200
        assert response.json["products"][0]["name"] == name_more_than_90_signs_long

    def test_404_when_the_page_is_too_high(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()

        with testing.assert_no_duplicated_queries():
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
                f"/public/offers/v1/products?venueId={venue.id}&limit=5&firstIndex=1"
            )
        assert response.status_code == 200
        assert response.json == {"products": []}

    def test_200_for_first_page_if_no_items(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()

        with testing.assert_no_duplicated_queries():
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
                f"/public/offers/v1/products?venueId={venue.id}&limit=5"
            )

        assert response.status_code == 200
        assert response.json == {
            "products": [],
        }

    def test_400_when_limit_is_too_high(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()

        with testing.assert_no_duplicated_queries():
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
                f"/public/offers/v1/products?venueId={venue.id}&limit=51"
            )

        assert response.status_code == 400
        assert response.json == {"limit": ["ensure this value is less than or equal to 50"]}

    def test_get_filtered_venue_offer(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()
        offer = offers_factories.ThingOfferFactory(venue=venue)
        offers_factories.ThingOfferFactory(
            venue__managingOfferer=venue.managingOfferer
        )  # offer attached to other venue

        with testing.assert_no_duplicated_queries():
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
                f"/public/offers/v1/products?venueId={venue.id}"
            )

        assert response.status_code == 200
        assert [product["id"] for product in response.json["products"]] == [offer.id]

    def test_get_offer_with_more_than_1000_description(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()
        offers_factories.ThingOfferFactory(venue=venue, description="a" * 1001)
        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
            f"/public/offers/v1/products?venueId={venue.id}"
        )
        assert response.status_code == 200

    def test_404_when_venue_id_not_tied_to_api_key(self, client):
        utils.create_offerer_provider_linked_to_venue()
        unrelated_venue = offerers_factories.VenueFactory()

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
            f"/public/offers/v1/products?venueId={unrelated_venue.id}"
        )

        assert response.status_code == 404

    def test_404_when_inactive_venue_provider(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue(is_venue_provider_active=False)
        offers_factories.ThingOfferFactory(venue=venue)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
            f"/public/offers/v1/products?venueId={venue.id}&limit=5"
        )

        assert response.status_code == 404
