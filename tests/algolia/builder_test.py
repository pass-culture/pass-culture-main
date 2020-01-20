from datetime import datetime

from algolia.builder import build_object
from models import EventType, PcObject
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_offerer, create_stock, create_venue
from tests.model_creators.specific_creators import create_offer_with_event_product, create_offer_with_thing_product


class BuildObjectTest:
    @clean_database
    def test_should_return_algolia_object_with_required_information(self, app):
        # Given
        beginning_datetime = datetime(2019, 11, 1, 10, 0, 0)
        end_datetime = datetime(2019, 12, 1, 10, 0, 0)
        offerer = create_offerer(name='Offerer name', idx=1)
        venue = create_venue(offerer=offerer,
                             city='Paris',
                             idx=2,
                             latitude=48.8638689,
                             longitude=2.3380198,
                             name='Venue name',
                             public_name='Venue public name')
        offer = create_offer_with_event_product(venue=venue,
                                                description='Un lit sous une rivière',
                                                idx=3,
                                                is_active=True,
                                                event_name='Event name',
                                                event_type=EventType.MUSIQUE)
        stock = create_stock(available=10,
                             beginning_datetime=beginning_datetime,
                             end_datetime=end_datetime,
                             offer=offer)
        PcObject.save(stock)

        # When
        result = build_object(offer)

        # Then
        assert result == {
            'objectID': 'AM',
            'offer': {
                'author': None,
                'dateRange': ['2019-11-01 10:00:00', '2019-12-01 10:00:00'],
                'description': 'Un lit sous une rivière',
                'id': 'AM',
                'isbn': None,
                'label': 'Concert ou festival',
                'name': 'Event name',
                'musicType': None,
                'performer': None,
                'showType': None,
                'speaker': None,
                'stageDirector': None,
                'thumbUrl': 'http://localhost/storage/thumbs/products/AE',
                'type': 'Écouter',
                'visa': None,
            },
            'offerer': {
                'name': 'Offerer name',
            },
            'venue': {
                'city': 'Paris',
                'name': 'Venue name',
                'publicName': 'Venue public name'
            },
            '_geoloc': {
                'lat': 48.86387,
                'lng': 2.33802
            }
        }

    @clean_database
    def test_should_return_an_author_when_exists(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer=offerer)
        offer = create_offer_with_thing_product(venue=venue)
        offer.extraData = {'author': 'MEFA'}
        stock = create_stock(offer=offer)
        PcObject.save(stock)

        # When
        result = build_object(offer)

        # Then
        assert result['offer']['author'] == 'MEFA'

    @clean_database
    def test_should_return_a_stage_director_when_exists(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer=offerer)
        offer = create_offer_with_thing_product(venue=venue)
        offer.extraData = {'stageDirector': 'MEFA'}
        stock = create_stock(offer=offer)
        PcObject.save(stock)

        # When
        result = build_object(offer)

        # Then
        assert result['offer']['stageDirector'] == 'MEFA'

    @clean_database
    def test_should_return_a_visa_when_exists(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer=offerer)
        offer = create_offer_with_thing_product(venue=venue)
        offer.extraData = {'visa': '123456789'}
        stock = create_stock(offer=offer)
        PcObject.save(stock)

        # When
        result = build_object(offer)

        # Then
        assert result['offer']['visa'] == '123456789'

    @clean_database
    def test_should_return_an_isbn_when_exists(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer=offerer)
        offer = create_offer_with_thing_product(venue=venue)
        offer.extraData = {'isbn': '123456789'}
        stock = create_stock(offer=offer)
        PcObject.save(stock)

        # When
        result = build_object(offer)

        # Then
        assert result['offer']['isbn'] == '123456789'

    @clean_database
    def test_should_return_a_speaker_when_exists(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer=offerer)
        offer = create_offer_with_thing_product(venue=venue)
        offer.extraData = {'speaker': 'MEFA'}
        stock = create_stock(offer=offer)
        PcObject.save(stock)

        # When
        result = build_object(offer)

        # Then
        assert result['offer']['speaker'] == 'MEFA'

    @clean_database
    def test_should_return_a_performer_when_exists(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer=offerer)
        offer = create_offer_with_thing_product(venue=venue)
        offer.extraData = {'performer': 'MEFA'}
        stock = create_stock(offer=offer)
        PcObject.save(stock)

        # When
        result = build_object(offer)

        # Then
        assert result['offer']['performer'] == 'MEFA'

    @clean_database
    def test_should_return_a_show_type_when_exists(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer=offerer)
        offer = create_offer_with_thing_product(venue=venue)
        offer.extraData = {'showType': 'dance'}
        stock = create_stock(offer=offer)
        PcObject.save(stock)

        # When
        result = build_object(offer)

        # Then
        assert result['offer']['showType'] == 'dance'

    @clean_database
    def test_should_return_a_music_type_when_exists(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer=offerer)
        offer = create_offer_with_thing_product(venue=venue)
        offer.extraData = {'musicType': 'jazz'}
        stock = create_stock(offer=offer)
        PcObject.save(stock)

        # When
        result = build_object(offer)

        # Then
        assert result['offer']['musicType'] == 'jazz'

    @clean_database
    def test_should_return_an_empty_date_range_when_offer_is_thing(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer=offerer)
        offer = create_offer_with_thing_product(venue=venue)
        stock = create_stock(offer=offer, is_soft_deleted=True)
        PcObject.save(stock)

        # When
        result = build_object(offer)

        # Then
        assert result['offer']['dateRange'] == []

    @clean_database
    def test_should_not_return_coordinates_when_one_coordinate_is_missing(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer=offerer, latitude=None, longitude=12.13)
        offer = create_offer_with_thing_product(venue=venue)
        stock = create_stock(offer=offer)
        PcObject.save(stock)

        # When
        result = build_object(offer)

        # Then
        assert '_geoloc' not in result
