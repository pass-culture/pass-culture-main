""" local providers test """
from unittest.mock import patch

import pytest

from local_providers import TiteLiveStocks
from models.pc_object import PcObject
from models.provider import Provider
from models.venue_provider import VenueProvider
from tests.conftest import clean_database
from utils.test_utils import create_offerer, create_venue, create_thing, create_thing_offer, provider_test

savedCounts = {}


@pytest.mark.standalone
@clean_database
@patch('local_providers.titelive_stocks.get_data')
def test_titelive_stock_provider(get_data, app):
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

    thing = create_thing(id_at_providers='0002730757438')
    offer = create_thing_offer(venue=venue, thing=thing)

    PcObject.check_and_save(thing, offer)

    assert venueProvider is not None
    provider_test(app,
                  TiteLiveStocks,
                  venueProvider,
                  checkedObjects=2,
                  createdObjects=1,
                  updatedObjects=0,
                  erroredObjects=0,
                  checkedThumbs=0,
                  createdThumbs=0,
                  updatedThumbs=0,
                  erroredThumbs=0,
                  Stock=1
                  )