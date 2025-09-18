import pytest

from pcapi.core import testing
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers import factories as offers_factories
from pcapi.core.providers import factories as providers_factories

from tests.routes.public.helpers import PublicAPIVenueEndpointHelper


@pytest.mark.usefixtures("db_session")
class GetProductsTest(PublicAPIVenueEndpointHelper):
    endpoint_url = "/public/offers/v1/products"
    endpoint_method = "get"

    num_queries_400 = 1  # select api_key, offerer and provider
    num_queries_400 += 1  # rollback atomic (at the end)
    num_queries_404 = num_queries_400 + 1  # check venue_provider exists

    num_queries_success_no_offers = 1  # select api_key, offerer and provider
    num_queries_success_no_offers += 1  # check venue_provider exists
    num_queries_success_no_offers += 1  # fetch offers

    num_queries_success = 1  # # select api_key, offerer and provider
    num_queries_success += 1  # check venue_provider exists
    num_queries_success += 1  # fetch offers
    num_queries_success += 1  # fetch stocks
    num_queries_success += 1  # fetch mediations
    num_queries_success += 1  # fetch price categories

    def test_should_raise_404_because_has_no_access_to_venue(self):
        plain_api_key, _ = self.setup_provider()
        venue_id = self.setup_venue().id

        with testing.assert_num_queries(self.num_queries_404):
            response = self.make_request(plain_api_key, query_params={"venue_id": venue_id})

            assert response.status_code == 404

    def test_should_raise_404_because_venue_provider_is_inactive(self):
        plain_api_key, venue_provider = self.setup_inactive_venue_provider()
        venue_id = venue_provider.venueId

        with testing.assert_num_queries(self.num_queries_404):
            response = self.make_request(plain_api_key, query_params={"venue_id": venue_id})
            assert response.status_code == 404

    def test_get_first_page(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        offers = offers_factories.ThingOfferFactory.create_batch(12, venue=venue_provider.venue)

        venue_id = venue_provider.venueId
        with testing.assert_num_queries(self.num_queries_success):
            response = self.make_request(plain_api_key, query_params={"venue_id": venue_id, "limit": 5})
            assert response.status_code == 200

        assert [product["id"] for product in response.json["products"]] == [offer.id for offer in offers[0:5]]

    def test_should_return_all_offers(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        venue2 = self.setup_venue()
        providers_factories.VenueProviderFactory(venue=venue2, provider=venue_provider.provider)
        offers = offers_factories.ThingOfferFactory.create_batch(
            12, venue=venue_provider.venue
        ) + offers_factories.ThingOfferFactory.create_batch(12, venue=venue2)
        offers_factories.ThingOfferFactory()

        no_check_on_venue_num_queries = self.num_queries_success - 1
        with testing.assert_num_queries(no_check_on_venue_num_queries):
            response = self.make_request(plain_api_key)
            assert response.status_code == 200

        assert [product["id"] for product in response.json["products"]] == [offer.id for offer in offers]

    def test_should_return_offers_linked_to_address_id(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        offerer_address_1 = offerers_factories.OffererAddressFactory(offerer=venue_provider.venue.managingOfferer)
        offerer_address_2 = offerers_factories.OffererAddressFactory(offerer=venue_provider.venue.managingOfferer)
        offerer_address_3 = offerers_factories.OffererAddressFactory(address=offerer_address_1.address)
        offer1 = offers_factories.ThingOfferFactory(venue=venue_provider.venue, offererAddress=offerer_address_1)
        offers_factories.ThingOfferFactory(venue=venue_provider.venue, offererAddress=offerer_address_2)
        offers_factories.ThingOfferFactory(offererAddress=offerer_address_3)

        with testing.assert_num_queries(self.num_queries_success):
            response = self.make_request(plain_api_key, query_params={"addressId": offerer_address_1.addressId})

            assert response.status_code == 200
            assert len(response.json["products"]) == 1

        assert response.json["products"][0]["id"] == offer1.id

    def test_get_last_page(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        offers = offers_factories.ThingOfferFactory.create_batch(12, venue=venue_provider.venue)

        venue_id = venue_provider.venueId
        first_index = offers[10].id
        with testing.assert_num_queries(self.num_queries_success):
            response = self.make_request(
                plain_api_key, query_params={"venue_id": venue_id, "limit": 5, "firstIndex": first_index}
            )
            assert response.status_code == 200

        assert [product["id"] for product in response.json["products"]] == [offer.id for offer in offers[10:12]]

    def test_get_product_using_ids_at_provider(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        id_at_provider_1 = "une"
        id_at_provider_2 = "belle"
        id_at_provider_3 = "têteDeVainqueur"

        offer_1 = offers_factories.OfferFactory(idAtProvider=id_at_provider_1, venue=venue_provider.venue)
        offer_2 = offers_factories.OfferFactory(idAtProvider=id_at_provider_2, venue=venue_provider.venue)
        offers_factories.OfferFactory(idAtProvider=id_at_provider_3, venue=venue_provider.venue)

        venue_id = venue_provider.venueId
        with testing.assert_num_queries(self.num_queries_success):
            response = self.make_request(
                plain_api_key,
                query_params={
                    "venue_id": venue_id,
                    "limit": 5,
                    "idsAtProvider": f"{id_at_provider_1},{id_at_provider_2}",
                },
            )
            assert response.status_code == 200

        assert [product["id"] for product in response.json["products"]] == [offer_1.id, offer_2.id]

    def test_should_return_200_even_if_the_offer_name_is_longer_than_90_signs_long(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        name_more_than_90_signs_long = (
            "Bébé, apprends-moi à devenir ton parent : naissance, sommeil, attachement, pleurs, développement"
        )
        offers_factories.ThingOfferFactory(venue=venue_provider.venue, name=name_more_than_90_signs_long)
        venue_id = venue_provider.venueId

        with testing.assert_num_queries(self.num_queries_success):
            response = self.make_request(plain_api_key, query_params={"venue_id": venue_id})
            assert response.status_code == 200

        assert response.json["products"][0]["name"] == name_more_than_90_signs_long

    def test_200_when_the_page_is_too_high(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()

        venue_id = venue_provider.venueId
        with testing.assert_num_queries(self.num_queries_success_no_offers):
            response = self.make_request(plain_api_key, query_params={"venue_id": venue_id, "firstIndex": 43})
            assert response.status_code == 200
            assert response.json == {"products": []}

    def test_200_for_first_page_if_no_items(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        venue_id = venue_provider.venueId
        with testing.assert_num_queries(self.num_queries_success_no_offers):
            response = self.make_request(plain_api_key, query_params={"venue_id": venue_id})
            assert response.status_code == 200
            assert response.json == {"products": []}

    @pytest.mark.parametrize(
        "query_params, expected_json",
        [
            ({"limit": 51}, {"limit": ["ensure this value is less than or equal to 50"]}),
            ({"limit": "test"}, {"limit": ["value is not a valid integer"]}),
            ({"venueId": "test"}, {"venueId": ["value is not a valid integer"]}),
            ({"addressId": "test"}, {"addressId": ["value is not a valid integer"]}),
        ],
    )
    def test_400_when_invalid_query_parameters(self, query_params, expected_json):
        plain_api_key, _ = self.setup_active_venue_provider()

        with testing.assert_num_queries(self.num_queries_400):
            response = self.make_request(plain_api_key, query_params=query_params)
            assert response.status_code == 400
            assert response.json == expected_json

    def test_get_filtered_venue_offer(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        offer = offers_factories.ThingOfferFactory(venue=venue_provider.venue)
        offers_factories.ThingOfferFactory(
            venue__managingOfferer=venue_provider.venue.managingOfferer
        )  # offer attached to other venue
        venue_id = venue_provider.venueId

        with testing.assert_num_queries(self.num_queries_success):
            response = self.make_request(plain_api_key, query_params={"venue_id": venue_id})

            assert response.status_code == 200

        assert [product["id"] for product in response.json["products"]] == [offer.id]

    def test_get_offer_with_more_than_1000_description(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        venue_id = venue_provider.venueId
        offers_factories.ThingOfferFactory(venue=venue_provider.venue, description="a" * 1001)

        with testing.assert_num_queries(self.num_queries_success):
            response = self.make_request(plain_api_key, query_params={"venue_id": venue_id})
            assert response.status_code == 200
