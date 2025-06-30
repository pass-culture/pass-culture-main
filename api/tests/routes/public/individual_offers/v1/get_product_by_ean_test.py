import datetime

import pytest
import time_machine

from pcapi.core import testing
from pcapi.core.categories import subcategories
from pcapi.core.offers import factories as offers_factories

from tests.routes.public.helpers import PublicAPIVenueEndpointHelper


@pytest.mark.usefixtures("db_session")
class GetProductByEanTest(PublicAPIVenueEndpointHelper):
    endpoint_url = "/public/offers/v1/products/ean"
    endpoint_method = "get"

    num_queries_400 = 1  # select api_key, offerer and provider
    num_queries_400 += 1  # rollback atomic (at the end)
    num_queries_404 = num_queries_400 + 1  # check venue_provider exists

    num_queries_success = 1  # select api_key, offerer and provider
    num_queries_success += 1  # check venue_provider exists
    num_queries_success += 1  # fetch offer
    num_queries_success += 1  # fetch stocks
    num_queries_success += 1  # fetch mediations
    num_queries_success += 1  # fetch price categories
    num_queries_success += 1  # FF WIP_REFACTO_FUTURE_OFFER

    def test_should_raise_404_because_has_no_access_to_venue(self):
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
            response = self.make_request(plain_api_key, query_params={"eans": ean, "venueId": venue_id})
            assert response.status_code == 404

    def test_should_raise_404_because_venue_provider_is_inactive(self):
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
            response = self.make_request(plain_api_key, query_params={"eans": ean, "venueId": venue_id})
            assert response.status_code == 404

    @time_machine.travel(datetime.datetime(2025, 6, 25, 12, 30, tzinfo=datetime.timezone.utc), tick=False)
    def test_valid_ean(self):
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
            response = self.make_request(plain_api_key, query_params={"eans": ean, "venueId": venue_id})
            assert response.status_code == 200

        assert response.json == {
            "products": [
                {
                    "bookingAllowedDatetime": None,
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
                    "publicationDatetime": "2025-06-25T12:25:00Z",
                    "name": "Vieux motard que jamais",
                    "status": "SOLD_OUT",
                    "stock": None,
                    "idAtProvider": None,
                }
            ]
        }

    @time_machine.travel(datetime.datetime(2025, 6, 25, 12, 30, tzinfo=datetime.timezone.utc), tick=False)
    def test_multiple_valid_eans(self):
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
            response = self.make_request(
                plain_api_key, query_params={"eans": f"{ean_1},{ean_2},{ean_3}", "venueId": venue_id}
            )
            assert response.status_code == 200

        assert response.json == {
            "products": [
                {
                    "bookingAllowedDatetime": None,
                    "publicationDatetime": "2025-06-25T12:25:00Z",
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
                    "bookingAllowedDatetime": None,
                    "publicationDatetime": "2025-06-25T12:25:00Z",
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
                    "bookingAllowedDatetime": None,
                    "publicationDatetime": "2025-06-25T12:25:00Z",
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

    def test_get_newest_ean_product(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        venue = venue_provider.venue
        venue_id = venue.id
        offers_factories.ThingOfferFactory(venue=venue, ean="1234567890123", isActive=False)
        newest_product_offer = offers_factories.ThingOfferFactory(venue=venue, ean="1234567890123", isActive=False)
        ean = newest_product_offer.ean

        with testing.assert_num_queries(self.num_queries_success):
            response = self.make_request(plain_api_key, query_params={"eans": ean, "venueId": venue_id})
            assert response.status_code == 200

        assert response.json["products"][0]["id"] == newest_product_offer.id

    @pytest.mark.parametrize("invalid_eans", ["123456789", "1234567891234,0123456789123,123455678,0987654321123"])
    def test_400_when_wrong_ean_format(self, invalid_eans):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        venue = venue_provider.venue
        venue_id = venue.id

        with testing.assert_num_queries(self.num_queries_400):
            response = self.make_request(plain_api_key, query_params={"eans": invalid_eans, "venueId": venue_id})
            assert response.status_code == 400

        assert response.json == {"eans": ["Only 13 characters EAN are accepted"]}

    def test_400_when_missing_venue_id(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        venue = venue_provider.venue
        product_offer = offers_factories.ThingOfferFactory(venue=venue, ean="1234567891234")
        ean = product_offer.ean

        with testing.assert_num_queries(self.num_queries_400):
            response = self.make_request(plain_api_key, query_params={"eans": ean})
            assert response.status_code == 400

        assert response.json == {"venueId": ["field required"]}

    def test_no_404_when_ean_not_found(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        venue = venue_provider.venue
        venue_id = venue.id
        offers_factories.ThingOfferFactory(
            venue=venue,
            description="Un livre de contrepèterie",
            name="Vieux motard que jamais",
        )

        with testing.assert_num_queries(self.num_queries_404):  # + fetch offer - rollback atomic
            response = self.make_request(plain_api_key, query_params={"eans": "1234567890123", "venueId": venue_id})
            assert response.status_code == 200

        assert response.json == {"products": []}

    @time_machine.travel(datetime.datetime(2025, 6, 25, 12, 30, tzinfo=datetime.timezone.utc), tick=False)
    def test_200_when_one_ean_in_list_not_found(self):
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
            response = self.make_request(
                plain_api_key, query_params={"eans": f"{ean},0123456789123", "venueId": venue_id}
            )
            assert response.status_code == 200

        assert response.json == {
            "products": [
                {
                    "bookingAllowedDatetime": None,
                    "publicationDatetime": "2025-06-25T12:25:00Z",
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

    def test_200_when_none_disabilities(self):
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
            response = self.make_request(plain_api_key, query_params={"eans": ean, "venueId": venue_id})
            assert response.status_code == 200

        assert response.json["products"][0]["accessibility"] == {
            "audioDisabilityCompliant": None,
            "mentalDisabilityCompliant": None,
            "motorDisabilityCompliant": None,
            "visualDisabilityCompliant": None,
        }

    def test_400_when_eans_list_is_empty(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        venue = venue_provider.venue
        venue_id = venue.id

        offers_factories.OfferFactory(venue=venue)

        with testing.assert_num_queries(self.num_queries_400):
            response = self.make_request(plain_api_key, query_params={"venueId": venue_id})
            assert response.status_code == 400

        assert response.json == {"eans": ["field required"]}
