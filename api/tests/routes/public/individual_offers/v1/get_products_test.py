import pytest

from pcapi.core import testing
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers import factories as offers_factories

from . import utils



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
        assert response.json["pagination"] == {
            "currentPage": 1,
            "itemsCount": 5,
            "itemsTotal": 12,
            "lastPage": 3,
            "limitPerPage": 5,
            "pagesLinks": {
                "current": f"{self.ENDPOINT_URL}?venueId={venue.id}&page=1&limit=5",
                "first": f"{self.ENDPOINT_URL}?venueId={venue.id}&page=1&limit=5",
                "last": f"{self.ENDPOINT_URL}?venueId={venue.id}&page=3&limit=5",
                "next": f"{self.ENDPOINT_URL}?venueId={venue.id}&page=2&limit=5",
                "previous": None,
            },
        }
        assert [product["id"] for product in response.json["products"]] == [offer.id for offer in offers[0:5]]

    def test_get_last_page(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()
        offers = offers_factories.ThingOfferFactory.create_batch(12, venue=venue)

        with testing.assert_no_duplicated_queries():
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
                f"/public/offers/v1/products?venueId={venue.id}&limit=5&page=3"
            )

        assert response.status_code == 200
        assert response.json["pagination"] == {
            "currentPage": 3,
            "itemsCount": 2,
            "itemsTotal": 12,
            "lastPage": 3,
            "limitPerPage": 5,
            "pagesLinks": {
                "current": f"{self.ENDPOINT_URL}?venueId={venue.id}&page=3&limit=5",
                "first": f"{self.ENDPOINT_URL}?venueId={venue.id}&page=1&limit=5",
                "last": f"{self.ENDPOINT_URL}?venueId={venue.id}&page=3&limit=5",
                "next": None,
                "previous": f"{self.ENDPOINT_URL}?venueId={venue.id}&page=2&limit=5",
            },
        }
        assert [product["id"] for product in response.json["products"]] == [offer.id for offer in offers[10:12]]

    def test_404_when_the_page_is_too_high(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()

        with testing.assert_no_duplicated_queries():
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
                f"/public/offers/v1/products?venueId={venue.id}&limit=5&page=2"
            )
        assert response.status_code == 404
        assert response.json == {
            "page": "The page you requested does not exist. The maximum page for the " "specified limit is 1"
        }

    def test_200_for_first_page_if_no_items(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()

        with testing.assert_no_duplicated_queries():
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
                f"/public/offers/v1/products?venueId={venue.id}&limit=5"
            )

        assert response.status_code == 200
        assert response.json == {
            "pagination": {
                "currentPage": 1,
                "itemsCount": 0,
                "itemsTotal": 0,
                "limitPerPage": 5,
                "lastPage": 1,
                "pagesLinks": {
                    "current": f"{self.ENDPOINT_URL}?venueId={venue.id}&page=1&limit=5",
                    "first": f"{self.ENDPOINT_URL}?venueId={venue.id}&page=1&limit=5",
                    "last": f"{self.ENDPOINT_URL}?venueId={venue.id}&page=1&limit=5",
                    "next": None,
                    "previous": None,
                },
            },
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
        assert response.json["pagination"] == {
            "currentPage": 1,
            "itemsCount": 1,
            "itemsTotal": 1,
            "lastPage": 1,
            "limitPerPage": 50,
            "pagesLinks": {
                "current": f"http://localhost/public/offers/v1/products?venueId={venue.id}&page=1&limit=50",
                "first": f"http://localhost/public/offers/v1/products?venueId={venue.id}&page=1&limit=50",
                "last": f"http://localhost/public/offers/v1/products?venueId={venue.id}&page=1&limit=50",
                "next": None,
                "previous": None,
            },
        }
        assert [product["id"] for product in response.json["products"]] == [offer.id]

    def test_404_when_venue_id_not_tied_to_api_key(self, client):
        utils.create_offerer_provider_linked_to_venue()
        unrelated_venue = offerers_factories.VenueFactory()

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
            f"/public/offers/v1/products?venueId={unrelated_venue.id}"
        )

        assert response.status_code == 404
