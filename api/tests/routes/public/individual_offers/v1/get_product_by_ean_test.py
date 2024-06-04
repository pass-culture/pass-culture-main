import pytest

from pcapi.core.categories import subcategories_v2 as subcategories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers import factories as offers_factories

from . import utils


@pytest.mark.usefixtures("db_session")
class GetProductByEanTest:
    def test_valid_ean(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()
        product_offer = offers_factories.ThingOfferFactory(
            venue=venue,
            subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id,
            description="Un livre de contrepèterie",
            name="Vieux motard que jamais",
            extraData={"ean": "1234567890123"},
        )

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
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
        venue, _ = utils.create_offerer_provider_linked_to_venue()
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

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
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
        venue, _ = utils.create_offerer_provider_linked_to_venue()
        offers_factories.ThingOfferFactory(venue=venue, extraData={"ean": "1234567890123"}, isActive=False)
        newest_product_offer = offers_factories.ThingOfferFactory(
            venue=venue, extraData={"ean": "1234567890123"}, isActive=False
        )

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
            f"/public/offers/v1/products/ean?eans={newest_product_offer.extraData['ean']}&venueId={venue.id}"
        )

        assert response.status_code == 200
        assert response.json["products"][0]["id"] == newest_product_offer.id

    def test_400_when_wrong_ean_format(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()
        product_offer = offers_factories.ThingOfferFactory(venue=venue, extraData={"ean": "123456789"})

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
            f"/public/offers/v1/products/ean?eans={product_offer.extraData['ean']}&venueId={venue.id}"
        )

        assert response.status_code == 400
        assert response.json == {"eans": ["Only 13 characters EAN are accepted"]}

    def test_400_when_one_wrong_ean_format_in_list(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()
        product_offer = offers_factories.ThingOfferFactory(venue=venue, extraData={"ean": "1234567891234"})
        product_offer_2 = offers_factories.ThingOfferFactory(venue=venue, extraData={"ean": "0123456789123"})
        product_offer_3 = offers_factories.ThingOfferFactory(venue=venue, extraData={"ean": "123455678"})
        product_offer_4 = offers_factories.ThingOfferFactory(venue=venue, extraData={"ean": "0987654321123"})

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
            f"/public/offers/v1/products/ean?eans={product_offer.extraData['ean']},{product_offer_2.extraData['ean']},{product_offer_3.extraData['ean']},{product_offer_4.extraData['ean']}&venueId={venue.id}"
        )

        assert response.status_code == 400
        assert response.json == {"eans": ["Only 13 characters EAN are accepted"]}

    def test_400_when_missing_venue_id(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()
        product_offer = offers_factories.ThingOfferFactory(venue=venue, extraData={"ean": "1234567891234"})

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
            f"/public/offers/v1/products/ean?eans={product_offer.extraData['ean']}"
        )

        assert response.status_code == 400
        assert response.json == {"venueId": ["field required"]}

    def test_no_404_when_ean_not_found(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()
        offers_factories.ThingOfferFactory(
            venue=venue,
            description="Un livre de contrepèterie",
            name="Vieux motard que jamais",
        )

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
            f"/public/offers/v1/products/ean?eans=1234567890123&venueId={venue.id}"
        )

        assert response.status_code == 200
        assert response.json == {"products": []}

    def test_error_when_inactive_venue_provider(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue(is_venue_provider_active=False)
        product_offer = offers_factories.ThingOfferFactory(
            venue=venue,
            description="Un livre de contrepèterie",
            name="Vieux motard que jamais",
            extraData={"ean": "1234567890123"},
        )

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
            f"/public/offers/v1/products/ean?eans={product_offer.extraData['ean']}&venueId={venue.id}"
        )

        assert response.status_code == 404
        assert response.json == {"venue_id": ["The venue could not be found"]}

    def test_200_when_one_ean_in_list_not_found(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()

        product_offer = offers_factories.ThingOfferFactory(
            venue=venue,
            subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id,
            description="Un livre de contrepèterie",
            name="Vieux motard que jamais",
            extraData={"ean": "1234567890123"},
        )

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
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
        venue, _ = utils.create_offerer_provider_linked_to_venue()

        product_offer = offers_factories.ThingOfferFactory(
            venue=venue,
            audioDisabilityCompliant=None,
            mentalDisabilityCompliant=None,
            motorDisabilityCompliant=None,
            visualDisabilityCompliant=None,
            extraData={"ean": "1234567890123"},
        )

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
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
        venue, _ = utils.create_offerer_provider_linked_to_venue()

        offers_factories.OfferFactory(
            venue=venue,
        )

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
            f"/public/offers/v1/products/ean?venueId={venue.id}"
        )

        assert response.status_code == 400
        assert response.json == {"eans": ["field required"]}
