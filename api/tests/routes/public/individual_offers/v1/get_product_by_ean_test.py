import pytest

from pcapi.core.categories import subcategories_v2 as subcategories
from pcapi.core.offers import factories as offers_factories

from tests.routes.public.helpers import PublicAPIVenueEndpointHelper


@pytest.mark.usefixtures("db_session")
class GetProductByEanTest(PublicAPIVenueEndpointHelper):
    endpoint_url = "/public/offers/v1/products/ean"

    def test_should_raise_401_because_not_authenticated(self, client):
        response = client.get(self.endpoint_url)
        assert response.status_code == 401

    def test_should_raise_404_because_has_no_access_to_venue(self, client):
        plain_api_key, _ = self.setup_provider()
        venue = self.setup_venue()
        product_offer = offers_factories.ThingOfferFactory(
            venue=venue,
            subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id,
            description="Un livre de contrepèterie",
            name="Vieux motard que jamais",
            extraData={"ean": "1234567890123"},
        )
        response = client.with_explicit_token(plain_api_key).get(
            f"{self.endpoint_url}?eans={product_offer.extraData['ean']}&venueId={venue.id}"
        )
        assert response.status_code == 404

    def test_should_raise_404_because_venue_provider_is_inactive(self, client):
        plain_api_key, venue_provider = self.setup_inactive_venue_provider()
        venue = venue_provider.venue
        product_offer = offers_factories.ThingOfferFactory(
            venue=venue,
            subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id,
            description="Un livre de contrepèterie",
            name="Vieux motard que jamais",
            extraData={"ean": "1234567890123"},
        )
        response = client.with_explicit_token(plain_api_key).get(
            f"{self.endpoint_url}?eans={product_offer.extraData['ean']}&venueId={venue.id}"
        )
        assert response.status_code == 404

    def test_valid_ean(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        venue = venue_provider.venue
        product_offer = offers_factories.ThingOfferFactory(
            venue=venue,
            subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id,
            description="Un livre de contrepèterie",
            name="Vieux motard que jamais",
            extraData={"ean": "1234567890123"},
        )

        response = client.with_explicit_token(plain_api_key).get(
            f"/public/offers/v1/products/ean?eans={product_offer.extraData['ean']}&venueId={venue.id}"
        )

        assert response.status_code == 200
        assert response.json == {
            "products": [
                {
                    "bookingContact": None,
                    "bookingEmail": None,
                    "categoryRelatedFields": {
                        "category": "SUPPORT_PHYSIQUE_FILM",
                        "ean": product_offer.extraData["ean"],
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
        product_offer = offers_factories.ThingOfferFactory(
            venue=venue,
            subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id,
            description="Un livre de contrepèterie",
            name="Vieux motard que jamais",
            extraData={"ean": "1234567890123"},
        )

        product_offer_2 = offers_factories.ThingOfferFactory(
            venue=venue,
            subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id,
            description="Un livre de poterie",
            name="Poterie pour les nuls",
            extraData={"ean": "0123456789123"},
        )

        product_offer_3 = offers_factories.ThingOfferFactory(
            venue=venue,
            subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id,
            description="Un CD",
            name="Pump it",
            extraData={"ean": "2345678901234"},
        )

        response = client.with_explicit_token(plain_api_key).get(
            f"/public/offers/v1/products/ean?eans={product_offer.extraData['ean']},{product_offer_2.extraData['ean']},{product_offer_3.extraData['ean']}&venueId={venue.id}"
        )

        assert response.status_code == 200
        assert response.json == {
            "products": [
                {
                    "bookingContact": None,
                    "bookingEmail": None,
                    "categoryRelatedFields": {
                        "category": "SUPPORT_PHYSIQUE_FILM",
                        "ean": product_offer_3.extraData["ean"],
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
                        "ean": product_offer_2.extraData["ean"],
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
                        "ean": product_offer.extraData["ean"],
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
        offers_factories.ThingOfferFactory(venue=venue, extraData={"ean": "1234567890123"}, isActive=False)
        newest_product_offer = offers_factories.ThingOfferFactory(
            venue=venue, extraData={"ean": "1234567890123"}, isActive=False
        )

        response = client.with_explicit_token(plain_api_key).get(
            f"/public/offers/v1/products/ean?eans={newest_product_offer.extraData['ean']}&venueId={venue.id}"
        )

        assert response.status_code == 200
        assert response.json["products"][0]["id"] == newest_product_offer.id

    def test_400_when_wrong_ean_format(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        venue = venue_provider.venue
        product_offer = offers_factories.ThingOfferFactory(venue=venue, extraData={"ean": "123456789"})

        response = client.with_explicit_token(plain_api_key).get(
            f"/public/offers/v1/products/ean?eans={product_offer.extraData['ean']}&venueId={venue.id}"
        )

        assert response.status_code == 400
        assert response.json == {"eans": ["Only 13 characters EAN are accepted"]}

    def test_400_when_one_wrong_ean_format_in_list(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        venue = venue_provider.venue
        product_offer = offers_factories.ThingOfferFactory(venue=venue, extraData={"ean": "1234567891234"})
        product_offer_2 = offers_factories.ThingOfferFactory(venue=venue, extraData={"ean": "0123456789123"})
        product_offer_3 = offers_factories.ThingOfferFactory(venue=venue, extraData={"ean": "123455678"})
        product_offer_4 = offers_factories.ThingOfferFactory(venue=venue, extraData={"ean": "0987654321123"})

        response = client.with_explicit_token(plain_api_key).get(
            f"/public/offers/v1/products/ean?eans={product_offer.extraData['ean']},{product_offer_2.extraData['ean']},{product_offer_3.extraData['ean']},{product_offer_4.extraData['ean']}&venueId={venue.id}"
        )

        assert response.status_code == 400
        assert response.json == {"eans": ["Only 13 characters EAN are accepted"]}

    def test_400_when_missing_venue_id(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        venue = venue_provider.venue
        product_offer = offers_factories.ThingOfferFactory(venue=venue, extraData={"ean": "1234567891234"})

        response = client.with_explicit_token(plain_api_key).get(
            f"/public/offers/v1/products/ean?eans={product_offer.extraData['ean']}"
        )

        assert response.status_code == 400
        assert response.json == {"venueId": ["field required"]}

    def test_no_404_when_ean_not_found(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        venue = venue_provider.venue
        offers_factories.ThingOfferFactory(
            venue=venue,
            description="Un livre de contrepèterie",
            name="Vieux motard que jamais",
        )

        response = client.with_explicit_token(plain_api_key).get(
            f"/public/offers/v1/products/ean?eans=1234567890123&venueId={venue.id}"
        )

        assert response.status_code == 200
        assert response.json == {"products": []}

    def test_200_when_one_ean_in_list_not_found(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        venue = venue_provider.venue

        product_offer = offers_factories.ThingOfferFactory(
            venue=venue,
            subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id,
            description="Un livre de contrepèterie",
            name="Vieux motard que jamais",
            extraData={"ean": "1234567890123"},
        )

        response = client.with_explicit_token(plain_api_key).get(
            f"/public/offers/v1/products/ean?eans={product_offer.extraData['ean']},0123456789123&venueId={venue.id}"
        )

        assert response.status_code == 200
        assert response.json == {
            "products": [
                {
                    "bookingContact": None,
                    "bookingEmail": None,
                    "categoryRelatedFields": {
                        "category": "SUPPORT_PHYSIQUE_FILM",
                        "ean": product_offer.extraData["ean"],
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

        product_offer = offers_factories.ThingOfferFactory(
            venue=venue,
            audioDisabilityCompliant=None,
            mentalDisabilityCompliant=None,
            motorDisabilityCompliant=None,
            visualDisabilityCompliant=None,
            extraData={"ean": "1234567890123"},
        )

        response = client.with_explicit_token(plain_api_key).get(
            f"/public/offers/v1/products/ean?eans={product_offer.extraData['ean']}&venueId={venue.id}"
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

        offers_factories.OfferFactory(venue=venue)

        response = client.with_explicit_token(plain_api_key).get(f"/public/offers/v1/products/ean?venueId={venue.id}")

        assert response.status_code == 400
        assert response.json == {"eans": ["field required"]}
