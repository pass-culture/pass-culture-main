from unittest.mock import patch, call

from local_providers import TiteLiveStocks
from models import Offer, Stock
from repository import repository
from repository.provider_queries import get_provider_by_local_class
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_stock, create_offerer, create_venue, create_venue_provider
from tests.model_creators.specific_creators import create_product_with_thing_type, create_offer_with_thing_product


@clean_database
@patch('local_providers.local_provider.feature_queries.is_active', return_value=True)
@patch('local_providers.local_provider.send_venue_provider_data_to_redis')
@patch('local_providers.titelive_stocks.get_stocks_information')
def test_titelive_stock_provider_create_1_stock_and_1_offer_with_wanted_attributes(stub_get_stocks_information,
                                                                                   stub_redis,
                                                                                   app):
    # Given
    stub_get_stocks_information.return_value = iter([{
        "ref": "0002730757438",
        "available": 10,
        "price": 4500,
        "validUntil": "2019-10-31T15:10:27Z"
    }])

    offerer = create_offerer()
    venue = create_venue(offerer)

    titelive_stocks_provider = get_provider_by_local_class('TiteLiveStocks')
    titelive_stocks_provider.isActive = True
    venue_provider = create_venue_provider(venue,
                                           titelive_stocks_provider, is_active=True,
                                           venue_id_at_offer_provider='77567146400110')
    product = create_product_with_thing_type(id_at_providers='0002730757438')
    repository.save(product, venue_provider)

    titelive_stocks = TiteLiveStocks(venue_provider)

    # When
    titelive_stocks.updateObjects()

    # Then
    offer = Offer.query.one()
    assert offer.type == product.type
    assert offer.name == product.name
    assert offer.description == product.description
    assert offer.venue is not None
    assert offer.bookingEmail == venue.bookingEmail
    assert offer.extraData == product.extraData
    stock = Stock.query.one()
    assert stock.bookingLimitDatetime is None
    assert stock.available == 10
    assert stock.price == 45


@clean_database
@patch('local_providers.local_provider.feature_queries.is_active', return_value=True)
@patch('local_providers.local_provider.send_venue_provider_data_to_redis')
@patch('local_providers.titelive_stocks.get_stocks_information')
def test_titelive_stock_provider_update_1_stock_and_1_offer(stub_get_stocks_information, stub_redis, app):
    # Given
    stub_get_stocks_information.return_value = iter([{
        "ref": "0002730757438",
        "available": 10,
        "price": 4500,
        "validUntil": "2019-10-31T15:10:27Z"
    }])

    offerer = create_offerer()
    venue = create_venue(offerer, siret='77567146400110')

    titelive_stocks_provider = get_provider_by_local_class('TiteLiveStocks')
    titelive_stocks_provider.isActive = True
    venue_provider = create_venue_provider(venue,
                                           titelive_stocks_provider, is_active=True,
                                           venue_id_at_offer_provider='77567146400110')
    product = create_product_with_thing_type(id_at_providers='0002730757438')
    offer = create_offer_with_thing_product(venue, product=product, id_at_providers='0002730757438@77567146400110')
    stock = create_stock(offer=offer, id_at_providers='0002730757438@77567146400110', available=2)
    repository.save(product, venue_provider, stock)

    titelive_stocks = TiteLiveStocks(venue_provider)

    # When
    titelive_stocks.updateObjects()

    # Then
    stock = Stock.query.one()
    assert stock.available == 10
    assert Offer.query.count() == 1


@clean_database
@patch('local_providers.local_provider.feature_queries.is_active', return_value=True)
@patch('local_providers.local_provider.send_venue_provider_data_to_redis')
@patch('local_providers.titelive_stocks.get_stocks_information')
def test_titelive_stock_provider_create_1_stock_and_update_1_existing_offer(stub_get_stocks_information,
                                                                            stub_redis,
                                                                            app):
    # Given
    stub_get_stocks_information.return_value = iter([{
        "ref": "0002730757438",
        "available": 10,
        "price": 4500,
        "validUntil": "2019-10-31T15:10:27Z"
    }])

    offerer = create_offerer()
    venue = create_venue(offerer, siret='77567146400110')

    titelive_stocks_provider = get_provider_by_local_class('TiteLiveStocks')
    titelive_stocks_provider.isActive = True
    venue_provider = create_venue_provider(venue,
                                           titelive_stocks_provider, is_active=True,
                                           venue_id_at_offer_provider='77567146400110')
    product = create_product_with_thing_type(id_at_providers='0002730757438')
    offer = create_offer_with_thing_product(venue, product=product, id_at_providers='0002730757438@77567146400110')
    repository.save(product, venue_provider, offer)

    titelive_stocks = TiteLiveStocks(venue_provider)

    # When
    titelive_stocks.updateObjects()

    # Then
    assert Stock.query.count() == 1
    assert Offer.query.count() == 1


@clean_database
@patch('local_providers.local_provider.feature_queries.is_active', return_value=True)
@patch('local_providers.local_provider.send_venue_provider_data_to_redis')
@patch('local_providers.titelive_stocks.get_stocks_information')
def test_titelive_stock_provider_create_2_stocks_and_2_offers_even_if_existing_offer_on_same_product(
        stub_get_stocks_information, stub_redis, app):
    # Given
    stub_get_stocks_information.side_effect = [
        iter([{
            "ref": "0002730757438",
            "available": 10,
            "price": 4500,
            "validUntil": "2019-10-31T15:10:27Z"
        }, {
            "ref": "0002736409898",
            "available": 2,
            "price": 100,
            "validUntil": "2019-10-31T15:10:27Z"
        }])
    ]

    offerer = create_offerer()
    venue = create_venue(offerer, siret='77567146400110')

    titelive_stocks_provider = get_provider_by_local_class('TiteLiveStocks')
    titelive_stocks_provider.isActive = True
    venue_provider = create_venue_provider(venue,
                                           titelive_stocks_provider, is_active=True,
                                           venue_id_at_offer_provider='77567146400110')
    product1 = create_product_with_thing_type(id_at_providers='0002730757438')
    product2 = create_product_with_thing_type(id_at_providers='0002736409898')
    offer = create_offer_with_thing_product(venue, product=product1, id_at_providers='not_titelive')
    repository.save(product1, product2, venue_provider, offer)

    titelive_stocks = TiteLiveStocks(venue_provider)

    # When
    titelive_stocks.updateObjects()

    # Then
    assert Offer.query.filter_by(lastProviderId=titelive_stocks_provider.id).count() == 2
    assert Stock.query.count() == 2


@clean_database
@patch('local_providers.local_provider.feature_queries.is_active', return_value=True)
@patch('local_providers.local_provider.send_venue_provider_data_to_redis')
@patch('local_providers.titelive_stocks.get_stocks_information')
def test_titelive_stock_provider_create_nothing_if_titelive_api_returns_no_results(stub_get_stocks_information,
                                                                                   stub_redis,
                                                                                   app):
    # Given
    stub_get_stocks_information.return_value = iter([])

    offerer = create_offerer()
    venue = create_venue(offerer, siret='77567146400110')

    titelive_stocks_provider = get_provider_by_local_class('TiteLiveStocks')
    titelive_stocks_provider.isActive = True
    venue_provider = create_venue_provider(venue,
                                           titelive_stocks_provider, is_active=True,
                                           venue_id_at_offer_provider='77567146400110')
    product = create_product_with_thing_type(id_at_providers='0002730757438')
    offer = create_offer_with_thing_product(venue, product=product)
    repository.save(product, venue_provider, offer)

    titelive_stocks = TiteLiveStocks(venue_provider)

    # When
    titelive_stocks.updateObjects()

    # Then
    assert Offer.query.filter_by(lastProviderId=titelive_stocks_provider.id).count() == 0
    assert Stock.query.count() == 0


@clean_database
@patch('local_providers.local_provider.feature_queries.is_active', return_value=True)
@patch('local_providers.local_provider.send_venue_provider_data_to_redis')
@patch('local_providers.titelive_stocks.get_stocks_information')
def test_titelive_stock_provider_deactivate_offer_if_stock_available_equals_0(stub_get_stocks_information,
                                                                              stub_redis,
                                                                              app):
    # Given
    stub_get_stocks_information.return_value = iter([{
        "ref": "0002730757438",
        "available": 0,
        "price": 4500,
        "validUntil": "2019-10-31T15:10:27Z"
    }])

    offerer = create_offerer()
    venue = create_venue(offerer, siret='77567146400110')

    titelive_stocks_provider = get_provider_by_local_class('TiteLiveStocks')
    titelive_stocks_provider.isActive = True
    venue_provider = create_venue_provider(venue,
                                           titelive_stocks_provider, is_active=True,
                                           venue_id_at_offer_provider='77567146400110')
    product = create_product_with_thing_type(id_at_providers='0002730757438')
    offer = create_offer_with_thing_product(venue, product=product, id_at_providers='0002730757438@77567146400110')
    stock = create_stock(offer=offer, id_at_providers='0002730757438@77567146400110')
    repository.save(product, venue_provider, stock)

    titelive_stocks = TiteLiveStocks(venue_provider)

    # When
    titelive_stocks.updateObjects()

    # Then
    offer = Offer.query.one()
    assert offer.isActive is False


@clean_database
@patch('local_providers.local_provider.feature_queries.is_active', return_value=True)
@patch('local_providers.local_provider.send_venue_provider_data_to_redis')
@patch('local_providers.titelive_stocks.get_stocks_information')
def test_titelive_stock_provider_iterates_over_pagination(stub_get_stocks_information, stub_redis, app):
    # Given
    stub_get_stocks_information.side_effect = [
        iter([{
            "ref": "0002730757438",
            "available": 0,
            "price": 4500,
            "validUntil": "2019-10-31T15:10:27Z"
        }]),
        iter([{
            "ref": "0002736409898",
            "available": 2,
            "price": 100,
            "validUntil": "2019-10-31T15:10:27Z"
        }])
    ]

    offerer = create_offerer()
    venue = create_venue(offerer, siret='77567146400110')

    titelive_stocks_provider = get_provider_by_local_class('TiteLiveStocks')
    titelive_stocks_provider.isActive = True
    venue_provider = create_venue_provider(venue,
                                           titelive_stocks_provider, is_active=True,
                                           venue_id_at_offer_provider='77567146400110')
    product1 = create_product_with_thing_type(id_at_providers='0002730757438')
    product2 = create_product_with_thing_type(id_at_providers='0002736409898')
    repository.save(product1, product2, venue_provider)

    titelive_stocks = TiteLiveStocks(venue_provider)

    # When
    titelive_stocks.updateObjects()

    # Then
    assert Offer.query.count() == 2
    assert Stock.query.count() == 2
    assert stub_get_stocks_information.call_args_list == [call('77567146400110', ''),
                                                          call('77567146400110', '0002730757438'),
                                                          call('77567146400110', '0002736409898')]


@clean_database
@patch('local_providers.local_provider.feature_queries.is_active', return_value=True)
@patch('local_providers.local_provider.send_venue_provider_data_to_redis')
@patch('local_providers.titelive_stocks.get_stocks_information')
def test_titelive_stock_provider_return_last_elements_as_last_seen_isbn(stub_get_stocks_information,
                                                                        stub_redis,
                                                                        app):
    # Given
    stub_get_stocks_information.return_value = iter([{
        "ref": "0002730757438",
        "available": 0,
        "price": 4500,
        "validUntil": "2019-10-31T15:10:27Z"
    }, {
        "ref": "0002736409898",
        "available": 2,
        "price": 100,
        "validUntil": "2019-10-31T15:10:27Z"
    }])

    offerer = create_offerer()
    venue = create_venue(offerer, siret='77567146400110')

    titelive_stocks_provider = get_provider_by_local_class('TiteLiveStocks')
    titelive_stocks_provider.isActive = True
    venue_provider = create_venue_provider(venue,
                                           titelive_stocks_provider, is_active=True,
                                           venue_id_at_offer_provider='77567146400110')
    titelive_stocks = TiteLiveStocks(venue_provider)

    # When
    titelive_stocks.updateObjects()

    # Then
    assert stub_get_stocks_information.call_count == 2
    assert titelive_stocks.last_seen_isbn == "0002736409898"


@clean_database
@patch('local_providers.local_provider.feature_queries.is_active', return_value=True)
@patch('local_providers.local_provider.send_venue_provider_data_to_redis')
@patch('local_providers.titelive_stocks.get_stocks_information')
def test_should_activate_offer_when_stocks_are_refilled(stub_get_stocks_information, stub_redis, app):
    # Given
    stub_get_stocks_information.side_effect = [
        iter([{
            "ref": "0002730757438",
            "available": 0,
            "price": 4500,
            "validUntil": "2019-10-31T15:10:27Z"
        }]),
        iter([{
            "ref": "0002730757438",
            "available": 2,
            "price": 4500,
            "validUntil": "2020-10-31T15:10:27Z"
        }])
    ]

    offerer = create_offerer()
    venue = create_venue(offerer)

    tite_live_things_provider = get_provider_by_local_class('TiteLiveThings')
    venue_provider = create_venue_provider(venue, tite_live_things_provider, is_active=True,
                                           venue_id_at_offer_provider='77567146400110')

    product = create_product_with_thing_type(id_at_providers='0002730757438')
    titelive_stocks_provider = get_provider_by_local_class('TiteLiveStocks')
    titelive_stocks_provider.isActive = True
    repository.save(product, titelive_stocks_provider, venue_provider)
    titelive_stocks = TiteLiveStocks(venue_provider)

    # When
    titelive_stocks.updateObjects()

    # Then
    offer = Offer.query.one()
    assert offer.isActive
