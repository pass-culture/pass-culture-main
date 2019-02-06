""" local providers test """
from unittest.mock import patch

import pytest

from local_providers import TiteLiveStocks
from models.pc_object import PcObject
from models.provider import Provider
from models.venue_provider import VenueProvider
from tests.conftest import clean_database
from tests.test_utils import create_offerer, create_venue, create_thing, create_thing_offer, provider_test
import requests

savedCounts = {}


def check_titelive_epagine_is_down():
    response = requests.get('https://stock.epagine.fr')
    response_text = str(response.content)
    successful_request = "running" in response_text
    status_code_not_200 = (response.status_code != 200)
    return not successful_request or status_code_not_200


@pytest.mark.standalone
@clean_database
@pytest.mark.skipif(check_titelive_epagine_is_down(), reason="Titelive Epagine API is down")
@patch('local_providers.titelive_stocks.get_data')
def test_titelive_stock_provider_create_1_stock_and_1_offer(get_data, app):
    # mock
    get_data.return_value = {
        'total': 'null',
        'limit': 5000,
        'stocks': [
            {
                "ref": "0002730757438",
                "available": 10,
                "price": 4500,
                "validUntil": "2019-10-31T15:10:27Z"
            }
        ]
    }
    # given
    offerer = create_offerer(siren='775671464')
    venue = create_venue(offerer, name='Librairie Titelive', siret='77567146400110')
    PcObject.check_and_save(venue)

    oa_provider = Provider.getByClassName('TiteLiveThings')
    venueProvider = VenueProvider()
    venueProvider.venue = venue
    venueProvider.provider = oa_provider
    venueProvider.isActive = True
    venueProvider.venueIdAtOfferProvider = '77567146400110'
    PcObject.check_and_save(venueProvider)
    venueProvider = VenueProvider.query \
        .filter_by(venueIdAtOfferProvider='77567146400110') \
        .one_or_none()

    thing = create_thing(id_at_providers='0002730757438')

    PcObject.check_and_save(thing)

    provider_test(app,
                  TiteLiveStocks,
                  venueProvider,
                  checkedObjects=2,
                  createdObjects=2,
                  updatedObjects=0,
                  erroredObjects=0,
                  checkedThumbs=0,
                  createdThumbs=0,
                  updatedThumbs=0,
                  erroredThumbs=0,
                  Stock=1,
                  Offer=1
                  )


@pytest.mark.standalone
@clean_database
@pytest.mark.skipif(check_titelive_epagine_is_down(), reason="Titelive Epagine API is down")
@patch('local_providers.titelive_stocks.get_data')
def test_titelive_stock_provider_create_1_stock_and_udpate_1_offer(get_data, app):
    # mock
    get_data.return_value = {
        'total': 'null',
        'limit': 5000,
        'stocks': [
            {
                "ref": "0002730757438",
                "available": 10,
                "price": 4500,
                "validUntil": "2019-10-31T15:10:27Z"
            }
        ]
    }
    # given
    offerer = create_offerer(siren='987654321')
    venue = create_venue(offerer, name='Librairie Titelive', siret='77567146400110')
    PcObject.check_and_save(venue)

    oa_provider = Provider.getByClassName('TiteLiveThings')
    venueProvider = VenueProvider()
    venueProvider.venue = venue
    venueProvider.provider = oa_provider
    venueProvider.isActive = True
    venueProvider.venueIdAtOfferProvider = '77567146400110'
    PcObject.check_and_save(venueProvider)
    venueProvider = VenueProvider.query \
        .filter_by(venueIdAtOfferProvider='77567146400110') \
        .one_or_none()

    thing = create_thing(id_at_providers='0002730757438')
    offer = create_thing_offer(venue, thing=thing)

    PcObject.check_and_save(thing, offer)

    provider_test(app,
                  TiteLiveStocks,
                  venueProvider,
                  checkedObjects=2,
                  createdObjects=1,
                  updatedObjects=1,
                  erroredObjects=0,
                  checkedThumbs=0,
                  createdThumbs=0,
                  updatedThumbs=0,
                  erroredThumbs=0,
                  Stock=1
                  )


@pytest.mark.standalone
@clean_database
@pytest.mark.skipif(check_titelive_epagine_is_down(), reason="Titelive Epagine API is down")
@patch('local_providers.titelive_stocks.get_data')
def test_titelive_stock_provider_create_2_stock_and_1_offer_and_udpate_1_offer(get_data, app):
    # mock
    get_data.return_value = {
        'total': 'null',
        'limit': 5000,
        'stocks': [
            {
                "ref": "0002730757438",
                "available": 10,
                "price": 4500,
                "validUntil": "2019-10-31T15:10:27Z"
            },
            {
                "ref": "0002736409898",
                "available": 2,
                "price": 100,
                "validUntil": "2019-10-31T15:10:27Z"
            }
        ]
    }
    # given
    offerer = create_offerer(siren='987654321')
    venue = create_venue(offerer, name='Librairie Titelive', siret='77567146400110')
    PcObject.check_and_save(venue)

    oa_provider = Provider.getByClassName('TiteLiveThings')
    venueProvider = VenueProvider()
    venueProvider.venue = venue
    venueProvider.provider = oa_provider
    venueProvider.isActive = True
    venueProvider.venueIdAtOfferProvider = '77567146400110'
    PcObject.check_and_save(venueProvider)
    venueProvider = VenueProvider.query \
        .filter_by(venueIdAtOfferProvider='77567146400110') \
        .one_or_none()

    thing_1 = create_thing(id_at_providers='0002730757438')
    thing_2 = create_thing(id_at_providers='0002736409898')
    offer = create_thing_offer(venue=venue, thing=thing_1)

    PcObject.check_and_save(thing_1, offer, thing_2)

    provider_test(app,
                  TiteLiveStocks,
                  venueProvider,
                  checkedObjects=4,
                  createdObjects=3,
                  updatedObjects=1,
                  erroredObjects=0,
                  checkedThumbs=0,
                  createdThumbs=0,
                  updatedThumbs=0,
                  erroredThumbs=0,
                  Stock=2,
                  Offer=1
                  )


@pytest.mark.standalone
@clean_database
@pytest.mark.skipif(check_titelive_epagine_is_down(), reason="Titelive Epagine API is down")
def test_titelive_stock_provider_create_nothing_if_siret_is_not_in_titelive_database(app):
    # given
    offerer = create_offerer(siren='987654321')
    venue = create_venue(offerer, name='Librairie Titelive', siret='12345678912345')
    PcObject.check_and_save(venue)

    oa_provider = Provider.getByClassName('TiteLiveThings')
    venueProvider = VenueProvider()
    venueProvider.venue = venue
    venueProvider.provider = oa_provider
    venueProvider.isActive = True
    venueProvider.venueIdAtOfferProvider = '12345678912345'

    PcObject.check_and_save(venueProvider)

    venueProvider = VenueProvider.query \
        .filter_by(venueIdAtOfferProvider='12345678912345') \
        .one_or_none()

    thing = create_thing(id_at_providers='0002730757438')
    offer = create_thing_offer(venue=venue, thing=thing)

    PcObject.check_and_save(thing, offer)

    provider_test(app,
                  TiteLiveStocks,
                  venueProvider,
                  checkedObjects=0,
                  createdObjects=0,
                  updatedObjects=0,
                  erroredObjects=0,
                  checkedThumbs=0,
                  createdThumbs=0,
                  updatedThumbs=0,
                  erroredThumbs=0,
                  Stock=0
                  )
