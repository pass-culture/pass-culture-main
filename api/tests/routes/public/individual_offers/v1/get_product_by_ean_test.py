import pytest

from pcapi.core import testing
from pcapi.core.categories import subcategories
from pcapi.core.offers import factories as offers_factories

from tests.routes.public.helpers import PublicAPIVenueEndpointHelper


@pytest.mark.usefixtures("db_session")
class GetProductByEanTest(PublicAPIVenueEndpointHelper):
    endpoint_url = "/public/offers/v1/products/ean"
    endpoint_method = "get"

    num_queries_400 = 1  # select api_key, offerer and provider
    num_queries_404 = num_queries_400 + 1  # check venue_provider exists

    # fetch offer (1 query)
    num_queries_offer_not_found = num_queries_404 + 1

    # fetch stocks (1 query)
    # fetch mediations (1 query)
    # fetch price categories (1 query)
    num_queries_success = num_queries_offer_not_found + 3

    def test_should_raise_404_because_has_no_access_to_venue(self, client):
        plain_api_key, _ = self.setup_provider()
        venue = self.setup_venue()
        venue_id = venue.id
        product_offer = offers_factories.ThingOfferFactory(
            venue=venue,
            subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id,
            description="Un livre de contrepèterie",
            name="Vieux motard que jamais",
            ean="1234567890123",
        )
        ean = product_offer.ean
        with testing.assert_num_queries(self.num_queries_404):
            response = client.with_explicit_token(plain_api_key).get(
                f"{self.endpoint_url}?eans={ean}&venueId={venue_id}"
            )
            assert response.status_code == 404

    def test_should_raise_404_because_venue_provider_is_inactive(self, client):
        plain_api_key, venue_provider = self.setup_inactive_venue_provider()
        venue = venue_provider.venue
        venue_id = venue.id
        product_offer = offers_factories.ThingOfferFactory(
            venue=venue,
            subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id,
            description="Un livre de contrepèterie",
            name="Vieux motard que jamais",
            ean="1234567890123",
        )
        ean = product_offer.ean
        with testing.assert_num_queries(self.num_queries_404):
            response = client.with_explicit_token(plain_api_key).get(
                f"{self.endpoint_url}?eans={ean}&venueId={venue_id}"
            )
            assert response.status_code == 404

    def test_valid_ean(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        venue = venue_provider.venue
        venue_id = venue.id
        product_offer = offers_factories.ThingOfferFactory(
            venue=venue,
            subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id,
            description="Un livre de contrepèterie",
            name="Vieux motard que jamais",
            ean="1234567890123",
        )
        ean = product_offer.ean
        with testing.assert_num_queries(self.num_queries_success):
            response = client.with_explicit_token(plain_api_key).get(
                f"/public/offers/v1/products/ean?eans={ean}&venueId={venue_id}"
            )
            assert response.status_code == 200

        assert response.json == {
            "products": [
                {
                    "bookingContact": None,
                    "bookingEmail": None,
                    "categoryRelatedFields": {
                        "category": "SUPPORT_PHYSIQUE_FILM",
                        "ean": product_offer.ean,
                    },
                    "description": "Un livre de contrepèterie",
                    "accessibility": {
                        "audioDisabilityCompliant": False,
                        "mentalDisabilityCompliant": False,
                        "motorDisabilityCompliant": False,
                        "visualDisabilityCompliant": False,
                    },
                    "enableDoubleBookings": False,
                    "externalTicketOfficeUrl": None,
                    "id": product_offer.id,
                    "image": None,
                    "itemCollectionDetails": None,
                    "location": {"type": "physical", "venueId": product_offer.venueId},
                    "name": "Vieux motard que jamais",
                    "status": "SOLD_OUT",
                    "stock": None,
                    "idAtProvider": None,
                }
            ]
        }

    def test_multiple_valid_eans(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        venue = venue_provider.venue
        venue_id = venue.id
        product_offer = offers_factories.ThingOfferFactory(
            venue=venue,
            subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id,
            description="Un livre de contrepèterie",
            name="Vieux motard que jamais",
            ean="1234567890123",
        )

        product_offer_2 = offers_factories.ThingOfferFactory(
            venue=venue,
            subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id,
            description="Un livre de poterie",
            name="Poterie pour les nuls",
            ean="0123456789123",
        )

        product_offer_3 = offers_factories.ThingOfferFactory(
            venue=venue,
            subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id,
            description="Un CD",
            name="Pump it",
            ean="2345678901234",
        )

        ean_1 = product_offer.ean
        ean_2 = product_offer_2.ean
        ean_3 = product_offer_3.ean

        with testing.assert_num_queries(self.num_queries_success):
            response = client.with_explicit_token(plain_api_key).get(
                f"/public/offers/v1/products/ean?eans={ean_1},{ean_2},{ean_3}&venueId={venue_id}"
            )
            assert response.status_code == 200

        assert response.json == {
            "products": [
                {
                    "bookingContact": None,
                    "bookingEmail": None,
                    "categoryRelatedFields": {
                        "category": "SUPPORT_PHYSIQUE_FILM",
                        "ean": product_offer_3.ean,
                    },
                    "description": "Un CD",
                    "accessibility": {
                        "audioDisabilityCompliant": False,
                        "mentalDisabilityCompliant": False,
                        "motorDisabilityCompliant": False,
                        "visualDisabilityCompliant": False,
                    },
                    "enableDoubleBookings": False,
                    "externalTicketOfficeUrl": None,
                    "id": product_offer_3.id,
                    "image": None,
                    "itemCollectionDetails": None,
                    "location": {"type": "physical", "venueId": product_offer_3.venueId},
                    "name": "Pump it",
                    "status": "SOLD_OUT",
                    "stock": None,
                    "idAtProvider": None,
                },
                {
                    "bookingContact": None,
                    "bookingEmail": None,
                    "categoryRelatedFields": {
                        "category": "SUPPORT_PHYSIQUE_FILM",
                        "ean": product_offer_2.ean,
                    },
                    "description": "Un livre de poterie",
                    "accessibility": {
                        "audioDisabilityCompliant": False,
                        "mentalDisabilityCompliant": False,
                        "motorDisabilityCompliant": False,
                        "visualDisabilityCompliant": False,
                    },
                    "enableDoubleBookings": False,
                    "externalTicketOfficeUrl": None,
                    "id": product_offer_2.id,
                    "image": None,
                    "itemCollectionDetails": None,
                    "location": {"type": "physical", "venueId": product_offer_2.venueId},
                    "name": "Poterie pour les nuls",
                    "status": "SOLD_OUT",
                    "stock": None,
                    "idAtProvider": None,
                },
                {
                    "bookingContact": None,
                    "bookingEmail": None,
                    "categoryRelatedFields": {
                        "category": "SUPPORT_PHYSIQUE_FILM",
                        "ean": product_offer.ean,
                    },
                    "description": "Un livre de contrepèterie",
                    "accessibility": {
                        "audioDisabilityCompliant": False,
                        "mentalDisabilityCompliant": False,
                        "motorDisabilityCompliant": False,
                        "visualDisabilityCompliant": False,
                    },
                    "enableDoubleBookings": False,
                    "externalTicketOfficeUrl": None,
                    "id": product_offer.id,
                    "image": None,
                    "itemCollectionDetails": None,
                    "location": {"type": "physical", "venueId": product_offer.venueId},
                    "name": "Vieux motard que jamais",
                    "status": "SOLD_OUT",
                    "stock": None,
                    "idAtProvider": None,
                },
            ]
        }

    def test_get_newest_ean_product(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        venue = venue_provider.venue
        venue_id = venue.id
        offers_factories.ThingOfferFactory(venue=venue, ean="1234567890123", isActive=False)
        newest_product_offer = offers_factories.ThingOfferFactory(venue=venue, ean="1234567890123", isActive=False)
        ean = newest_product_offer.ean

        with testing.assert_num_queries(self.num_queries_success):
            response = client.with_explicit_token(plain_api_key).get(
                f"/public/offers/v1/products/ean?eans={ean}&venueId={venue_id}"
            )
            assert response.status_code == 200

        assert response.json["products"][0]["id"] == newest_product_offer.id

    def test_400_when_wrong_ean_format(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        venue = venue_provider.venue
        venue_id = venue.id

        with testing.assert_num_queries(self.num_queries_400):
            response = client.with_explicit_token(plain_api_key).get(
                f"/public/offers/v1/products/ean?eans=123456789&venueId={venue_id}"
            )

            assert response.status_code == 400

        assert response.json == {"eans": ["Only 13 characters EAN are accepted"]}

    def test_400_when_one_wrong_ean_format_in_list(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        venue = venue_provider.venue
        venue_id = venue.id

        with testing.assert_num_queries(self.num_queries_400):
            response = client.with_explicit_token(plain_api_key).get(
                f"/public/offers/v1/products/ean?eans=1234567891234,0123456789123,123455678,0987654321123&venueId={venue_id}"
            )
            assert response.status_code == 400

        assert response.json == {"eans": ["Only 13 characters EAN are accepted"]}

    def test_400_when_missing_venue_id(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        venue = venue_provider.venue
        product_offer = offers_factories.ThingOfferFactory(venue=venue, ean="1234567891234")
        ean = product_offer.ean

        with testing.assert_num_queries(self.num_queries_400):
            response = client.with_explicit_token(plain_api_key).get(f"/public/offers/v1/products/ean?eans={ean}")

            assert response.status_code == 400

        assert response.json == {"venueId": ["field required"]}

    def test_no_404_when_ean_not_found(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        venue = venue_provider.venue
        venue_id = venue.id
        offers_factories.ThingOfferFactory(
            venue=venue,
            description="Un livre de contrepèterie",
            name="Vieux motard que jamais",
        )

        with testing.assert_num_queries(self.num_queries_offer_not_found):
            response = client.with_explicit_token(plain_api_key).get(
                f"/public/offers/v1/products/ean?eans=1234567890123&venueId={venue_id}"
            )
            assert response.status_code == 200

        assert response.json == {"products": []}

    def test_200_when_one_ean_in_list_not_found(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        venue = venue_provider.venue
        venue_id = venue.id

        product_offer = offers_factories.ThingOfferFactory(
            venue=venue,
            subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id,
            description="Un livre de contrepèterie",
            name="Vieux motard que jamais",
            ean="1234567890123",
        )
        ean = product_offer.ean

        with testing.assert_num_queries(self.num_queries_success):
            response = client.with_explicit_token(plain_api_key).get(
                f"/public/offers/v1/products/ean?eans={ean},0123456789123&venueId={venue_id}"
            )
            assert response.status_code == 200

        assert response.json == {
            "products": [
                {
                    "bookingContact": None,
                    "bookingEmail": None,
                    "categoryRelatedFields": {
                        "category": "SUPPORT_PHYSIQUE_FILM",
                        "ean": product_offer.ean,
                    },
                    "description": "Un livre de contrepèterie",
                    "accessibility": {
                        "audioDisabilityCompliant": False,
                        "mentalDisabilityCompliant": False,
                        "motorDisabilityCompliant": False,
                        "visualDisabilityCompliant": False,
                    },
                    "enableDoubleBookings": False,
                    "externalTicketOfficeUrl": None,
                    "id": product_offer.id,
                    "image": None,
                    "itemCollectionDetails": None,
                    "location": {"type": "physical", "venueId": product_offer.venueId},
                    "name": "Vieux motard que jamais",
                    "status": "SOLD_OUT",
                    "stock": None,
                    "idAtProvider": None,
                }
            ]
        }

    def test_200_when_none_disabilities(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        venue = venue_provider.venue
        venue_id = venue.id

        product_offer = offers_factories.ThingOfferFactory(
            venue=venue,
            audioDisabilityCompliant=None,
            mentalDisabilityCompliant=None,
            motorDisabilityCompliant=None,
            visualDisabilityCompliant=None,
            ean="1234567890123",
        )
        ean = product_offer.ean

        with testing.assert_num_queries(self.num_queries_success):
            response = client.with_explicit_token(plain_api_key).get(
                f"/public/offers/v1/products/ean?eans={ean}&venueId={venue_id}"
            )
            assert response.status_code == 200

        assert response.json["products"][0]["accessibility"] == {
            "audioDisabilityCompliant": None,
            "mentalDisabilityCompliant": None,
            "motorDisabilityCompliant": None,
            "visualDisabilityCompliant": None,
        }

    def test_400_when_eans_list_is_empty(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        venue = venue_provider.venue
        venue_id = venue.id

        offers_factories.OfferFactory(venue=venue)

        with testing.assert_num_queries(self.num_queries_400):
            response = client.with_explicit_token(plain_api_key).get(
                f"/public/offers/v1/products/ean?venueId={venue_id}"
            )
            assert response.status_code == 400

        assert response.json == {"eans": ["field required"]}
