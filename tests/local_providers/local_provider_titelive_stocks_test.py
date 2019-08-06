""" local providers test """
from unittest.mock import patch

import pytest
import requests

from local_providers import TiteLiveStocks
from models import Offer, Stock
from models.pc_object import PcObject
from models.venue_provider import VenueProvider
from repository.provider_queries import get_provider_by_local_class
from tests.conftest import clean_database
from tests.test_utils import create_offerer, create_venue, create_product_with_thing_type, \
    create_offer_with_thing_product, provider_test, create_stock

savedCounts = {}


def check_titelive_epagine_is_down():
    response = requests.get('https://stock.epagine.fr')
    response_text = str(response.content)
    successful_request = "running" in response_text
    status_code_not_200 = (response.status_code != 200)
    return not successful_request or status_code_not_200


@clean_database
@patch('local_providers.titelive_stocks.get_data')
def test_titelive_stock_provider_create_1_stock_and_1_offer(get_data, app):
    # given
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

    offerer = create_offerer(siren='775671464')
    venue = create_venue(offerer, name='Librairie Titelive', siret='77567146400110')
    PcObject.save(venue)

    tite_live_things_provider = get_provider_by_local_class('TiteLiveThings')
    venue_provider = VenueProvider()
    venue_provider.venue = venue
    venue_provider.provider = tite_live_things_provider
    venue_provider.isActive = True
    venue_provider.venueIdAtOfferProvider = '77567146400110'
    PcObject.save(venue_provider)

    product = create_product_with_thing_type(id_at_providers='0002730757438')
    PcObject.save(product)

    # When / Then
    provider_test(app,
                  TiteLiveStocks,
                  venue_provider,
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

    offer = Offer.query.one()
    assert offer.type == product.type
    assert offer.name == product.name
    assert offer.description == product.description
    assert offer.venue is not None
    assert offer.bookingEmail is None
    assert offer.extraData == product.extraData
    stock = Stock.query.one()
    assert stock.bookingLimitDatetime is None
    assert stock.available == 10
    assert stock.price == 45


@clean_database
@patch('local_providers.titelive_stocks.get_data')
def test_titelive_stock_provider_update_1_stock_and_1_offer(get_data, app):
    # given
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

    offerer = create_offerer(siren='987654321')
    venue = create_venue(offerer, name='Librairie Titelive', siret='77567146400110')
    PcObject.save(venue)

    tite_live_things_provider = get_provider_by_local_class('TiteLiveThings')
    venue_provider = VenueProvider()
    venue_provider.venue = venue
    venue_provider.provider = tite_live_things_provider
    venue_provider.isActive = True
    venue_provider.venueIdAtOfferProvider = '77567146400110'
    PcObject.save(venue_provider)

    product = create_product_with_thing_type(id_at_providers='0002730757438')
    offer = create_offer_with_thing_product(venue, product=product, id_at_providers='0002730757438@77567146400110')
    stock = create_stock(offer=offer, id_at_providers='0002730757438@77567146400110')
    PcObject.save(product, offer, stock)

    # When / Then
    provider_test(app,
                  TiteLiveStocks,
                  venue_provider,
                  checkedObjects=2,
                  createdObjects=0,
                  updatedObjects=2,
                  erroredObjects=0,
                  checkedThumbs=0,
                  createdThumbs=0,
                  updatedThumbs=0,
                  erroredThumbs=0,
                  )


@clean_database
@patch('local_providers.titelive_stocks.get_data')
def test_titelive_stock_provider_create_1_stock_and_update_1_existing_offer(get_data, app):
    # given
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

    offerer = create_offerer(siren='987654321')
    venue = create_venue(offerer, name='Librairie Titelive', siret='77567146400110')
    PcObject.save(venue)

    tite_live_things_provider = get_provider_by_local_class('TiteLiveThings')
    venue_provider = VenueProvider()
    venue_provider.venue = venue
    venue_provider.provider = tite_live_things_provider
    venue_provider.isActive = True
    venue_provider.venueIdAtOfferProvider = '77567146400110'
    PcObject.save(venue_provider)

    product = create_product_with_thing_type(id_at_providers='0002730757438')
    offer = create_offer_with_thing_product(venue, product=product, id_at_providers='0002730757438@77567146400110')
    PcObject.save(product, offer)

    # When / Then
    provider_test(app,
                  TiteLiveStocks,
                  venue_provider,
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


@clean_database
@patch('local_providers.titelive_stocks.get_data')
def test_titelive_stock_provider_create_2_stock_and_2_offer_even_if_existing_offer_on_same_product(get_data, app):
    # given
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

    offerer = create_offerer(siren='987654321')
    venue = create_venue(offerer, name='Librairie Titelive', siret='77567146400110')
    PcObject.save(venue)

    tite_live_things_provider = get_provider_by_local_class('TiteLiveThings')
    venue_provider = VenueProvider()
    venue_provider.venue = venue
    venue_provider.provider = tite_live_things_provider
    venue_provider.isActive = True
    venue_provider.venueIdAtOfferProvider = '77567146400110'
    PcObject.save(venue_provider)

    thing_1 = create_product_with_thing_type(id_at_providers='0002730757438')
    thing_2 = create_product_with_thing_type(id_at_providers='0002736409898')
    offer = create_offer_with_thing_product(venue=venue, product=thing_1, id_at_providers="not_titelive")
    PcObject.save(thing_1, offer, thing_2)

    # When / Then
    provider_test(app,
                  TiteLiveStocks,
                  venue_provider,
                  checkedObjects=4,
                  createdObjects=4,
                  updatedObjects=0,
                  erroredObjects=0,
                  checkedThumbs=0,
                  createdThumbs=0,
                  updatedThumbs=0,
                  erroredThumbs=0,
                  Stock=2,
                  Offer=2
                  )


@clean_database
@pytest.mark.skipif(check_titelive_epagine_is_down(), reason="Titelive Epagine API is down")
def test_titelive_stock_provider_create_nothing_if_siret_is_not_in_titelive_database(app):
    # given
    offerer = create_offerer(siren='987654321')
    venue = create_venue(offerer, name='Librairie Titelive', siret='12345678912345')
    PcObject.save(venue)

    tite_live_things_provider = get_provider_by_local_class('TiteLiveThings')
    venue_provider = VenueProvider()
    venue_provider.venue = venue
    venue_provider.provider = tite_live_things_provider
    venue_provider.isActive = True
    venue_provider.venueIdAtOfferProvider = '12345678912345'
    PcObject.save(venue_provider)

    product = create_product_with_thing_type(id_at_providers='0002730757438')
    offer = create_offer_with_thing_product(venue=venue, product=product)
    PcObject.save(product, offer)

    # When / Then
    provider_test(app,
                  TiteLiveStocks,
                  venue_provider,
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
