from repository import repository
from sandboxes.scripts.getters.webapp_08_booking import get_non_free_thing_offer_with_active_mediation, \
    get_non_free_event_offer
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_offerer, create_venue, create_stock, create_mediation
from tests.model_creators.specific_creators import create_offer_with_thing_product, create_product_with_thing_type, \
    create_product_with_event_type, create_offer_with_event_product
from utils.date import format_into_ISO_8601
from utils.human_ids import humanize


class GetNonFreeThingOfferWithActiveMediationTest:
    @clean_database
    def test_should_not_return_payload_when_offer_is_not_bookable(self, app):
        # Given
        offerer = create_offerer(validation_token='validation_token')
        venue = create_venue(offerer)
        product = create_product_with_thing_type()
        offer = create_offer_with_thing_product(venue, product=product)
        stock = create_stock(offer=offer)
        mediation = create_mediation(offer)
        repository.save(mediation, stock)

        # When
        offer_json_response = get_non_free_thing_offer_with_active_mediation()

        # Then
        assert offer_json_response == {}


class GetNonFreeEventOfferTest:
    @clean_database
    def test_should_return_expected_payload_for_bookable_offer(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        product = create_product_with_event_type()
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
                'ageMax': None,
                'ageMin': None,
                'baseScore': 0,
                'bookingEmail': 'booking@example.net',
                'conditions': None,
                'dateCreated': format_into_ISO_8601(offer.dateCreated),
                'dateModifiedAtLastProvider': format_into_ISO_8601(offer.dateModifiedAtLastProvider),
                'description': None,
                'durationMinutes': 60,
                'extraData': None,
                'fieldsUpdated': [],
                'id': humanize(offer.id),
                'idAtProviders': offer.idAtProviders,
                'isActive': True,
                'isDuo': False,
                'isNational': False,
                'keywordsString': 'Test event',
                'lastProviderId': None,
                'mediaUrls': [],
                'name': 'Test event',
                'productId': humanize(product.id),
                'thingName': 'Test event',
                'type': 'EventType.SPECTACLE_VIVANT',
                'url': None,
                'venueCity': 'Montreuil',
                'venueId': humanize(venue.id),
                'venueName': 'La petite librairie',
                'withdrawalDetails': None
            }
        }

    @clean_database
    def test_should_not_return_payload_when_offer_is_not_bookable(self, app):
        # Given
        offerer = create_offerer(validation_token='validation_token')
        venue = create_venue(offerer)
        product = create_product_with_event_type()
        offer = create_offer_with_event_product(venue, product=product)
        stock = create_stock(offer=offer)
        mediation = create_mediation(offer)
        repository.save(mediation, stock)

        # When
        offer_json_response = get_non_free_event_offer()

        # Then
        assert offer_json_response == {}
