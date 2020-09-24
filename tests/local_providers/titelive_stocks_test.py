from datetime import date, datetime, timedelta
from unittest.mock import call, patch

from freezegun import freeze_time

from local_providers import TiteLiveStocks
from models import OfferSQLEntity, StockSQLEntity
from repository import repository
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_booking, create_offerer, create_stock, create_user, \
    create_venue, create_venue_provider
from tests.model_creators.provider_creators import activate_provider
from tests.model_creators.specific_creators import create_offer_with_thing_product, create_product_with_thing_type


class TiteliveStocksTest:
    class NextTest:
        @clean_database
        @patch('local_providers.titelive_stocks.titelive_stocks.api_titelive_stocks.stocks_information')
        def test_should_return_providable_infos_with_correct_data(self, mock_titelive_api_response, app):
            # Given
            mock_titelive_api_response.return_value = iter([{
                "ref": "0002730757438",
                "available": 10,
                "price": 4500,
                "validUntil": "2019-10-31T15:10:27Z"
            }])

            offerer = create_offerer()
            venue = create_venue(offerer, siret='12345678912345')
            titelive_provider = activate_provider('TiteLiveStocks')
            venue_provider = create_venue_provider(venue, titelive_provider, venue_id_at_offer_provider=venue.siret,
                                                   last_sync_date=datetime(2020, 2, 4))
            product = create_product_with_thing_type(id_at_providers='0002730757438')
            repository.save(product, venue_provider)

            titelive_stocks = TiteLiveStocks(venue_provider)

            # When
            titelive_providable_infos = next(titelive_stocks)

            # Then
            assert mock_titelive_api_response.call_args_list == [
                call('12345678912345', '', datetime(2020, 2, 4))
            ]
            assert len(titelive_providable_infos) == 2

            offer_providable_info = titelive_providable_infos[0]
            stock_providable_info = titelive_providable_infos[1]

            assert offer_providable_info.type == OfferSQLEntity
            assert offer_providable_info.id_at_providers == '0002730757438@12345678912345'
            assert stock_providable_info.type == StockSQLEntity
            assert stock_providable_info.id_at_providers == '0002730757438@12345678912345'

    class UpdateObjectsTest:
        @clean_database
        @patch('local_providers.titelive_stocks.titelive_stocks.api_titelive_stocks.stocks_information')
        def test_titelive_stock_provider_create_1_stock_and_1_offer_with_wanted_attributes(self,
                                                                                           stub_get_stocks_information,
                                                                                           app):
            # Given
            stub_get_stocks_information.return_value = iter([{
                "ref": "0002730757438",
                "available": 10,
                "price": 4500,
                "validUntil": "2019-10-31T15:10:27Z"
            }])

            offerer = create_offerer()
            venue = create_venue(offerer, siret='12345678912345')
            titelive_provider = activate_provider('TiteLiveStocks')
            venue_provider = create_venue_provider(venue, titelive_provider, venue_id_at_offer_provider=venue.siret,
                                                   last_sync_date=datetime(2020, 2, 4))
            product = create_product_with_thing_type(id_at_providers='0002730757438')
            repository.save(product, venue_provider)

            titelive_stocks = TiteLiveStocks(venue_provider)

            # When
            titelive_stocks.updateObjects()

            # Then
            offer = OfferSQLEntity.query.first()
            stock = StockSQLEntity.query.first()

            assert offer.type == product.type
            assert offer.description == product.description
            assert offer.venue is not None
            assert offer.bookingEmail == venue.bookingEmail
            assert offer.extraData == product.extraData

            assert stock.price == 45.00
            assert stock.quantity == 10
            assert stock.bookingLimitDatetime is None

        @clean_database
        @patch('local_providers.titelive_stocks.titelive_stocks.api_titelive_stocks.stocks_information')
        def test_titelive_stock_provider_update_1_stock_and_1_offer(self, stub_get_stocks_information, app):
            # Given
            stub_get_stocks_information.return_value = iter([{
                "ref": "0002730757438",
                "available": 10,
                "price": 4500,
                "validUntil": "2019-10-31T15:10:27Z"
            }])

            offerer = create_offerer()
            venue = create_venue(offerer, siret='77567146400110')

            titelive_stocks_provider = activate_provider('TiteLiveStocks')
            venue_provider = create_venue_provider(venue,
                                                   titelive_stocks_provider, is_active=True,
                                                   venue_id_at_offer_provider='77567146400110')
            product = create_product_with_thing_type(id_at_providers='02730757438')
            offer = create_offer_with_thing_product(venue, product=product,
                                                    id_at_providers='0002730757438@77567146400110')
            stock = create_stock(id_at_providers='0002730757438@77567146400110', offer=offer, quantity=10)
            repository.save(product, venue_provider, stock)

            titelive_stocks = TiteLiveStocks(venue_provider)

            # When
            titelive_stocks.updateObjects()

            # Then
            stock = StockSQLEntity.query.one()
            assert stock.quantity == 10
            assert OfferSQLEntity.query.count() == 1

        @freeze_time('2019-01-03 12:00:00')
        @clean_database
        @patch('local_providers.titelive_stocks.titelive_stocks.api_titelive_stocks.stocks_information')
        def test_titelive_stock_provider_always_update_the_stock_modification_date(self, stub_get_stocks_information,
                                                                                   app):
            # Given
            stub_get_stocks_information.return_value = iter([{
                "ref": "0002730757438",
                "available": 2,
                "price": 4500,
                "validUntil": "2019-10-31T15:10:27Z"
            }])

            offerer = create_offerer()
            venue = create_venue(offerer, siret='77567146400110')

            titelive_stocks_provider = activate_provider('TiteLiveStocks')
            venue_provider = create_venue_provider(venue,
                                                   titelive_stocks_provider, is_active=True,
                                                   venue_id_at_offer_provider='77567146400110')
            product = create_product_with_thing_type(id_at_providers='0002730757438')
            offer = create_offer_with_thing_product(venue, product=product,
                                                    id_at_providers='0002730757438@77567146400110')
            yesterday = date.today() - timedelta(days=1)
            stock = create_stock(date_modified=yesterday, id_at_providers='0002730757438@77567146400110', offer=offer,
                                 quantity=2)
            repository.save(product, venue_provider, stock)

            titelive_stocks = TiteLiveStocks(venue_provider)

            # When
            titelive_stocks.updateObjects()

            # Then
            stock = StockSQLEntity.query.one()
            assert stock.dateModified == datetime.now()

        @clean_database
        @patch('local_providers.titelive_stocks.titelive_stocks.api_titelive_stocks.stocks_information')
        def test_titelive_stock_provider_create_1_stock_and_update_1_existing_offer(self, stub_get_stocks_information,

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

            titelive_stocks_provider = activate_provider('TiteLiveStocks')
            venue_provider = create_venue_provider(venue,
                                                   titelive_stocks_provider, is_active=True,
                                                   venue_id_at_offer_provider='77567146400110')
            product = create_product_with_thing_type(id_at_providers='0002730757438')
            offer = create_offer_with_thing_product(venue, product=product,
                                                    id_at_providers='0002730757438@77567146400110')
            repository.save(product, venue_provider, offer)

            titelive_stocks = TiteLiveStocks(venue_provider)

            # When
            titelive_stocks.updateObjects()

            # Then
            assert StockSQLEntity.query.count() == 1
            assert OfferSQLEntity.query.count() == 1

        @clean_database
        @patch('local_providers.titelive_stocks.titelive_stocks.api_titelive_stocks.stocks_information')
        def test_titelive_stock_provider_create_2_stocks_and_2_offers_even_if_existing_offer_on_same_product(
                self, mock_stocks_information, app):
            # Given
            mock_stocks_information.return_value = iter([{
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

            offerer = create_offerer()
            venue = create_venue(offerer, siret='77567146400110')

            titelive_stocks_provider = activate_provider('TiteLiveStocks')
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
            assert OfferSQLEntity.query.filter_by(lastProviderId=titelive_stocks_provider.id).count() == 2
            assert StockSQLEntity.query.count() == 2

        @clean_database
        @patch('local_providers.titelive_stocks.titelive_stocks.api_titelive_stocks.stocks_information')
        def test_titelive_stock_provider_create_nothing_if_titelive_api_returns_no_results(self,
                                                                                           stub_get_stocks_information,
                                                                                           app):
            # Given
            stub_get_stocks_information.return_value = iter([])

            offerer = create_offerer()
            venue = create_venue(offerer, siret='77567146400110')

            titelive_stocks_provider = activate_provider('TiteLiveStocks')
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
            assert OfferSQLEntity.query.filter_by(lastProviderId=titelive_stocks_provider.id).count() == 0
            assert StockSQLEntity.query.count() == 0

        @clean_database
        @patch('local_providers.titelive_stocks.titelive_stocks.api_titelive_stocks.stocks_information')
        def test_titelive_stock_provider_iterates_over_pagination(self, stub_get_stocks_information, app):
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

            titelive_stocks_provider = activate_provider('TiteLiveStocks')
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
            assert OfferSQLEntity.query.count() == 2
            assert StockSQLEntity.query.count() == 2
            assert stub_get_stocks_information.call_args_list == [call('77567146400110', '', None),
                                                                  call('77567146400110', '0002730757438', None),
                                                                  call('77567146400110', '0002736409898', None)]

        @clean_database
        @patch('local_providers.titelive_stocks.titelive_stocks.api_titelive_stocks.stocks_information')
        def should_call_api_with_venue_siret_and_last_sync_date(self, stub_get_stocks_information, app):
            # Given
            stub_get_stocks_information.side_effect = [
                iter([{
                    "ref": "0002730757438",
                    "available": 0,
                    "price": 4500,
                    "validUntil": "2019-10-31T15:10:27Z"
                }])
            ]

            offerer = create_offerer()
            venue = create_venue(offerer, siret='77567146400110')

            titelive_stocks_provider = activate_provider('TiteLiveStocks')
            last_sync_date = datetime.strptime('27/08/2020 09:15:32', '%d/%m/%Y %H:%M:%S')
            venue_provider = create_venue_provider(venue,
                                                   titelive_stocks_provider, is_active=True,
                                                   venue_id_at_offer_provider='77567146400110',
                                                   last_sync_date=last_sync_date)
            product = create_product_with_thing_type(id_at_providers='0002730757438')
            repository.save(product, venue_provider)

            titelive_stocks = TiteLiveStocks(venue_provider)

            # When
            titelive_stocks.updateObjects()

            # Then
            assert stub_get_stocks_information.call_args_list == [call('77567146400110', '', last_sync_date),
                                                                  call('77567146400110', '0002730757438',
                                                                       last_sync_date)]

        @clean_database
        @patch('local_providers.titelive_stocks.titelive_stocks.api_titelive_stocks.stocks_information')
        def test_titelive_stock_provider_return_last_elements_as_last_seen_isbn(self, stub_get_stocks_information,

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

            titelive_stocks_provider = activate_provider('TiteLiveStocks')
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
        @patch('local_providers.titelive_stocks.titelive_stocks.api_titelive_stocks.stocks_information')
        def test_should_not_create_offer_when_product_is_not_gcu_compatible(self, stub_get_stocks_information,
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

            titelive_stocks_provider = activate_provider('TiteLiveStocks')
            venue_provider = create_venue_provider(venue,
                                                   titelive_stocks_provider, is_active=True,
                                                   venue_id_at_offer_provider='77567146400110')
            product = create_product_with_thing_type(id_at_providers='0002730757438', is_gcu_compatible=False)
            repository.save(product, venue_provider)

            titelive_stocks = TiteLiveStocks(venue_provider)

            # When
            titelive_stocks.updateObjects()

            # Then
            assert OfferSQLEntity.query.count() == 0
            assert StockSQLEntity.query.count() == 0

        @clean_database
        @patch('local_providers.titelive_stocks.titelive_stocks.api_titelive_stocks.stocks_information')
        def test_titelive_stock_provider_available_stock_is_sum_of_updated_available_and_bookings(self,
                                                                                                  stub_get_stocks_information,
                                                                                                  app):
            # Given
            stub_get_stocks_information.side_effect = [
                iter([{
                    "ref": "9780199536986",
                    "available": 5,
                    "price": 0,
                }])
            ]
            offerer = create_offerer()
            venue = create_venue(offerer, siret='12345678912345')
            titelive_stocks_provider = activate_provider('TiteLiveStocks')
            venue_provider = create_venue_provider(
                venue,
                titelive_stocks_provider,
                is_active=True,
                venue_id_at_offer_provider='12345678912345'
            )
            product = create_product_with_thing_type(id_at_providers='9780199536986')

            offer = create_offer_with_thing_product(venue, product=product,
                                                    id_at_providers='9780199536986@12345678912345')

            stock = create_stock(id_at_providers='9780199536986@12345678912345', offer=offer, price=0, quantity=20)

            booking = create_booking(
                user=create_user(),
                quantity=1,
                stock=stock
            )

            repository.save(venue_provider, booking)

            stub_get_stocks_information.side_effect = [
                iter([{
                    "ref": "9780199536986",
                    "available": 66,
                    "price": 0,
                }])
            ]

            titelive_stocks = TiteLiveStocks(venue_provider)

            # When
            titelive_stocks.updateObjects()

            # Then
            stock = StockSQLEntity.query.one()
            assert stock.quantity == 67
