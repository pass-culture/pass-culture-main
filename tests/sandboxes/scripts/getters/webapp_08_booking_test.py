import pytest

from pcapi.model_creators.generic_creators import create_mediation
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_stock
from pcapi.model_creators.generic_creators import create_venue
from pcapi.model_creators.specific_creators import create_offer_with_event_product
from pcapi.model_creators.specific_creators import create_offer_with_thing_product
from pcapi.model_creators.specific_creators import create_product_with_event_subcategory
from pcapi.model_creators.specific_creators import create_product_with_thing_subcategory
from pcapi.repository import repository
from pcapi.sandboxes.scripts.getters.webapp_08_booking import get_non_free_event_offer
from pcapi.sandboxes.scripts.getters.webapp_08_booking import get_non_free_thing_offer_with_active_mediation
from pcapi.utils.date import format_into_utc_date
from pcapi.utils.human_ids import humanize


class GetNonFreeThingOfferWithActiveMediationTest:
    @pytest.mark.usefixtures("db_session")
    def test_should_return_expected_payload_for_bookable_offer(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        product = create_product_with_thing_subcategory()
        offer = create_offer_with_thing_product(venue, product=product)
        stock = create_stock(offer=offer)
        mediation = create_mediation(offer)
        repository.save(mediation, stock)

        # When
        offer_json_response = get_non_free_thing_offer_with_active_mediation()

        # Then
        assert offer_json_response == {
            "mediationId": humanize(mediation.id),
            "offer": {
                "ageMax": None,
                "ageMin": None,
                "authorId": None,
                "audioDisabilityCompliant": None,
                "bookingEmail": "booking@example.net",
                "conditions": None,
                "dateCreated": format_into_utc_date(offer.dateCreated),
                "dateModifiedAtLastProvider": format_into_utc_date(offer.dateModifiedAtLastProvider),
                "description": None,
                "durationMinutes": None,
                "externalTicketOfficeUrl": None,
                "extraData": {"author": "Test Author"},
                "fieldsUpdated": [],
                "id": humanize(offer.id),
                "idAtProvider": offer.idAtProvider,
                "idAtProviders": offer.idAtProviders,
                "isActive": True,
                "isDuo": False,
                "isEducational": False,
                "isNational": False,
                "dateUpdated": format_into_utc_date(offer.dateUpdated),
                "lastProviderId": None,
                "lastValidationDate": None,
                "mediaUrls": ["test/urls"],
                "mentalDisabilityCompliant": None,
                "motorDisabilityCompliant": None,
                "name": "Test Book",
                "productId": humanize(product.id),
                "rankingWeight": None,
                "status": "ACTIVE",
                "subcategoryId": "LIVRE_PAPIER",
                "thingName": "Test Book",
                "url": None,
                "validation": "APPROVED",
                "venueCity": "Montreuil",
                "venueId": humanize(venue.id),
                "venueName": "La petite librairie",
                "visualDisabilityCompliant": None,
                "withdrawalDetails": None,
            },
        }

    @pytest.mark.usefixtures("db_session")
    def test_should_not_return_payload_when_offer_is_not_bookable(self, app):
        # Given
        offerer = create_offerer(validation_token="validation_token")
        venue = create_venue(offerer)
        product = create_product_with_thing_subcategory()
        offer = create_offer_with_thing_product(venue, product=product)
        stock = create_stock(offer=offer)
        mediation = create_mediation(offer)
        repository.save(mediation, stock)

        # When
        offer_json_response = get_non_free_thing_offer_with_active_mediation()

        # Then
        assert offer_json_response == {}


class GetNonFreeEventOfferTest:
    @pytest.mark.usefixtures("db_session")
    def test_should_return_expected_payload_for_bookable_offer(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        product = create_product_with_event_subcategory()
        offer = create_offer_with_event_product(venue, product=product)
        stock = create_stock(offer=offer)
        mediation = create_mediation(offer)
        repository.save(mediation, stock)

        # When
        offer_json_response = get_non_free_event_offer()

        # Then
        assert offer_json_response == {
            "mediationId": humanize(mediation.id),
            "offer": {
                "ageMax": None,
                "ageMin": None,
                "authorId": None,
                "audioDisabilityCompliant": None,
                "bookingEmail": "booking@example.net",
                "conditions": None,
                "dateCreated": format_into_utc_date(offer.dateCreated),
                "dateModifiedAtLastProvider": format_into_utc_date(offer.dateModifiedAtLastProvider),
                "description": None,
                "durationMinutes": 60,
                "externalTicketOfficeUrl": None,
                "extraData": None,
                "fieldsUpdated": [],
                "id": humanize(offer.id),
                "idAtProvider": None,
                "idAtProviders": offer.idAtProviders,
                "isActive": True,
                "isDuo": False,
                "isEducational": False,
                "isNational": False,
                "dateUpdated": format_into_utc_date(offer.dateUpdated),
                "lastProviderId": None,
                "lastValidationDate": None,
                "mediaUrls": [],
                "mentalDisabilityCompliant": None,
                "motorDisabilityCompliant": None,
                "name": "Test event",
                "productId": humanize(product.id),
                "rankingWeight": None,
                "status": "ACTIVE",
                "subcategoryId": "SPECTACLE_REPRESENTATION",
                "thingName": "Test event",
                "url": None,
                "validation": "APPROVED",
                "venueCity": "Montreuil",
                "venueId": humanize(venue.id),
                "venueName": "La petite librairie",
                "visualDisabilityCompliant": None,
                "withdrawalDetails": None,
            },
        }

    @pytest.mark.usefixtures("db_session")
    def test_should_not_return_payload_when_offer_is_not_bookable(self, app):
        # Given
        offerer = create_offerer(validation_token="validation_token")
        venue = create_venue(offerer)
        product = create_product_with_event_subcategory()
        offer = create_offer_with_event_product(venue, product=product)
        stock = create_stock(offer=offer)
        mediation = create_mediation(offer)
        repository.save(mediation, stock)

        # When
        offer_json_response = get_non_free_event_offer()

        # Then
        assert offer_json_response == {}
