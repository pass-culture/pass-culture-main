import pytest

from pcapi.core import testing
from pcapi.core.offers import factories as offers_factories

from tests.routes.public.helpers import PublicAPIVenueEndpointHelper


@pytest.mark.usefixtures("db_session")
class GetProductsTest(PublicAPIVenueEndpointHelper):
    endpoint_url = "/public/offers/v1/products"

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
            "%s?venueId=%s" % (self.endpoint_url, venue_provider.venueId)
        )
        assert response.status_code == 404

    def test_get_first_page(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        offers = offers_factories.ThingOfferFactory.create_batch(12, venue=venue_provider.venue)

        with testing.assert_no_duplicated_queries():
            response = client.with_explicit_token(plain_api_key).get(
                f"/public/offers/v1/products?venueId={venue_provider.venueId}&limit=5"
            )

        assert response.status_code == 200
        assert [product["id"] for product in response.json["products"]] == [offer.id for offer in offers[0:5]]

    def test_get_last_page(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        offers = offers_factories.ThingOfferFactory.create_batch(12, venue=venue_provider.venue)

        with testing.assert_no_duplicated_queries():
            response = client.with_explicit_token(plain_api_key).get(
                f"/public/offers/v1/products?venueId={venue_provider.venueId}&limit=5&firstIndex={int(offers[10].id)}"
            )

        assert response.status_code == 200
        assert [product["id"] for product in response.json["products"]] == [offer.id for offer in offers[10:12]]

    def test_get_product_using_ids_at_provider(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        id_at_provider_1 = "une"
        id_at_provider_2 = "belle"
        id_at_provider_3 = "têteDeVainqueur"

        offer_1 = offers_factories.OfferFactory(idAtProvider=id_at_provider_1, venue=venue_provider.venue)
        offer_2 = offers_factories.OfferFactory(idAtProvider=id_at_provider_2, venue=venue_provider.venue)
        offers_factories.OfferFactory(idAtProvider=id_at_provider_3, venue=venue_provider.venue)

        with testing.assert_no_duplicated_queries():
            response = client.with_explicit_token(plain_api_key).get(
                f"/public/offers/v1/products?venueId={venue_provider.venueId}&limit=5&idsAtProvider={id_at_provider_1},{id_at_provider_2}"
            )

        assert response.status_code == 200
        assert [product["id"] for product in response.json["products"]] == [offer_1.id, offer_2.id]

    def test_should_return_a_200_event_if_the_offer_name_is_longer_than_90_signs_long(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        name_more_than_90_signs_long = (
            "Bébé, apprends-moi à devenir ton parent : naissance, sommeil, attachement, pleurs, développement"
        )
        offers_factories.ThingOfferFactory(venue=venue_provider.venue, name=name_more_than_90_signs_long)

        with testing.assert_no_duplicated_queries():
            response = client.with_explicit_token(plain_api_key).get(
                f"/public/offers/v1/products?venueId={venue_provider.venueId}"
            )

        assert response.status_code == 200
        assert response.json["products"][0]["name"] == name_more_than_90_signs_long

    def test_404_when_the_page_is_too_high(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()

        with testing.assert_no_duplicated_queries():
            response = client.with_explicit_token(plain_api_key).get(
                f"/public/offers/v1/products?venueId={venue_provider.venueId}&limit=5&firstIndex=1"
            )
        assert response.status_code == 200
        assert response.json == {"products": []}

    def test_200_for_first_page_if_no_items(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()

        with testing.assert_no_duplicated_queries():
            response = client.with_explicit_token(plain_api_key).get(
                f"/public/offers/v1/products?venueId={venue_provider.venueId}&limit=5"
            )

        assert response.status_code == 200
        assert response.json == {
            "products": [],
        }

    def test_400_when_limit_is_too_high(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()

        with testing.assert_no_duplicated_queries():
            response = client.with_explicit_token(plain_api_key).get(
                f"/public/offers/v1/products?venueId={venue_provider.venueId}&limit=51"
            )

        assert response.status_code == 400
        assert response.json == {"limit": ["ensure this value is less than or equal to 50"]}

    def test_get_filtered_venue_offer(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        offer = offers_factories.ThingOfferFactory(venue=venue_provider.venue)
        offers_factories.ThingOfferFactory(
            venue__managingOfferer=venue_provider.venue.managingOfferer
        )  # offer attached to other venue

        with testing.assert_no_duplicated_queries():
            response = client.with_explicit_token(plain_api_key).get(
                f"/public/offers/v1/products?venueId={venue_provider.venueId}"
            )

        assert response.status_code == 200
        assert [product["id"] for product in response.json["products"]] == [offer.id]

    def test_get_offer_with_more_than_1000_description(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        offers_factories.ThingOfferFactory(venue=venue_provider.venue, description="a" * 1001)
        response = client.with_explicit_token(plain_api_key).get(
            f"/public/offers/v1/products?venueId={venue_provider.venueId}"
        )
        assert response.status_code == 200
