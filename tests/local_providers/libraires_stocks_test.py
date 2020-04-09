from unittest.mock import patch, call

from local_providers.libraires_stocks import LibrairesStocks
from models import Offer, StockSQLEntity
from repository import repository
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_venue_provider, create_venue, create_offerer, create_stock, \
    create_booking, create_user
from tests.model_creators.provider_creators import activate_provider
from tests.model_creators.specific_creators import create_product_with_thing_type, create_offer_with_thing_product


class LibrairesStocksTest:
    class NextTest:
        @clean_database
        @patch('local_providers.libraires_stocks.get_libraires_stock_information')
        def test_should_return_providable_infos_with_correct_data(self, mock_libraires_api_response, app):
            # Given
            mock_libraires_api_response.return_value = iter([
                {
                    "ref": "9780199536986",
                    "available": 1,
                    "price": 6.36
                }
            ])

            offerer = create_offerer()
            venue = create_venue(offerer, siret='12345678912345')
            libraires_provider = activate_provider('LibrairesStocks')
            venue_provider = create_venue_provider(venue, libraires_provider)
            product = create_product_with_thing_type(id_at_providers='9780199536986')

            repository.save(venue_provider, product)

            libraires_stocks_provider = LibrairesStocks(venue_provider)

            # When
            libraires_providable_infos = next(libraires_stocks_provider)

            # Then
            assert mock_libraires_api_response.call_args_list == [call('12345678912345', '', '')]
            assert len(libraires_providable_infos) == 2

            offer_providable_info = libraires_providable_infos[0]
            stock_providable_info = libraires_providable_infos[1]

            assert offer_providable_info.type == Offer
            assert offer_providable_info.id_at_providers == '9780199536986@12345678912345'
            assert stock_providable_info.type == StockSQLEntity
            assert stock_providable_info.id_at_providers == '9780199536986@12345678912345'

    class UpdateObjectsTest:
        @clean_database
        @patch('local_providers.libraires_stocks.get_libraires_stock_information')
        def test_libraires_stock_provider_create_one_stock_and_one_offer_with_wanted_attributes(self,
                                                                                                mock_libraires_api_response,
                                                                                                app):
            # Given
            mock_libraires_api_response.return_value = iter([{
                "ref": "9780199536986",
                "available": 10,
                "price": 16.5
            }])

            offerer = create_offerer()
            venue = create_venue(offerer, siret='77567146400110')

            libraires_stocks_provider = activate_provider('LibrairesStocks')
            venue_provider = create_venue_provider(venue, libraires_stocks_provider, is_active=True,
                                                   venue_id_at_offer_provider='77567146400110')
            product = create_product_with_thing_type(id_at_providers='9780199536986')
            repository.save(product, venue_provider)

            libraires_stocks = LibrairesStocks(venue_provider)

            # When
            libraires_stocks.updateObjects()

            # Then
            offer = Offer.query.first()
            stock = StockSQLEntity.query.first()

            assert offer.type == product.type
            assert offer.description == product.description
            assert offer.venue is not None
            assert offer.bookingEmail == venue.bookingEmail
            assert offer.extraData == product.extraData

            assert stock.price == 16.5
            assert stock.quantity == 10
            assert stock.bookingLimitDatetime is None

        @clean_database
        @patch('local_providers.libraires_stocks.get_libraires_stock_information')
        def test_libraires_stock_provider_update_one_stock_and_update_matching_offer(self, mock_libraires_api_response,
                                                                                     app):
            # Given
            mock_libraires_api_response.return_value = iter([{
                "ref": "9780199536986",
                "available": 10,
                "price": 16
            }])

            offerer = create_offerer()
            venue = create_venue(offerer)

            libraires_stocks_provider = activate_provider('LibrairesStocks')
            venue_provider = create_venue_provider(venue, libraires_stocks_provider, is_active=True,
                                                   venue_id_at_offer_provider='12345678912345')
            product = create_product_with_thing_type(id_at_providers='9780199536986')
            offer = create_offer_with_thing_product(venue, product=product,
                                                    id_at_providers='9780199536986@12345678912345')
            stock = create_stock(quantity=20, id_at_providers='9780199536986@12345678912345', offer=offer)

            repository.save(product, offer, stock)
            libraires_stocks = LibrairesStocks(venue_provider)

            # When
            libraires_stocks.updateObjects()

            # Then
            stock = StockSQLEntity.query.one()
            assert stock.quantity == 10
            assert Offer.query.count() == 1

        @clean_database
        @patch('local_providers.libraires_stocks.get_libraires_stock_information')
        def test_libraires_stocks_create_2_stocks_and_2_offers_even_if_existing_offer_on_same_product(self,
                                                                                                      mock_libraires_api_response,
                                                                                                      app):
            # Given
            mock_libraires_api_response.return_value = iter([{
                "ref": "9780199536986",
                "available": 5,
                "price": 16
            }, {"ref": "1550199555555",
                "available": 4,
                "price": 18
                }])

            offerer = create_offerer()
            venue = create_venue(offerer, siret='12345678912345')

            libraires_stocks_provider = activate_provider('LibrairesStocks')
            venue_provider = create_venue_provider(venue, libraires_stocks_provider, is_active=True,
                                                   venue_id_at_offer_provider='12345678912345')
            product_1 = create_product_with_thing_type(id_at_providers='9780199536986')
            product_2 = create_product_with_thing_type(id_at_providers='1550199555555')
            offer = create_offer_with_thing_product(venue, product=product_2,
                                                    id_at_providers='everything_but_libraires')

            repository.save(offer, product_1, product_2, venue_provider)

            libraires_stocks = LibrairesStocks(venue_provider)

            # When
            libraires_stocks.updateObjects()

            # Then
            assert StockSQLEntity.query.count() == 2
            assert Offer.query.filter_by(lastProviderId=libraires_stocks_provider.id).count() == 2
            assert libraires_stocks.last_processed_isbn == '1550199555555'

        @clean_database
        @patch('local_providers.libraires_stocks.get_libraires_stock_information')
        def test_libraires_stock_provider_available_stock_is_sum_of_updated_available_and_bookings(self,
                                                                                                   mock_libraires_api_response,
                                                                                                   app):
            # Given
            mock_libraires_api_response.return_value = iter([{
                "ref": "9780199536986",
                "available": 5,
                "price": 0
            }])

            offerer = create_offerer()
            venue = create_venue(offerer, siret='12345678912345')
            libraires_stocks_provider = activate_provider('LibrairesStocks')
            venue_provider = create_venue_provider(
                venue,
                libraires_stocks_provider,
                is_active=True,
                venue_id_at_offer_provider='12345678912345'
            )
            product = create_product_with_thing_type(id_at_providers='9780199536986')

            offer = create_offer_with_thing_product(venue, product=product,
                                                    id_at_providers='9780199536986@12345678912345')

            stock = create_stock(quantity=20, id_at_providers='9780199536986@12345678912345', offer=offer, price=0)

            booking = create_booking(
                user=create_user(),
                quantity=1,
                stock=stock
            )

            repository.save(venue_provider, booking)

            mock_libraires_api_response.return_value = iter([{
                "ref": "9780199536986",
                "available": 66,
                "price": 0
            }])

            libraires_stocks = LibrairesStocks(venue_provider)

            # When
            libraires_stocks.updateObjects()

            # Then
            stock = StockSQLEntity.query.one()
            assert stock.quantity == 67

    class WhenSynchronizedTwiceTest:
        @clean_database
        @patch('local_providers.libraires_stocks.get_libraires_stock_information')
        def test_libraires_stock_provider_iterates_over_pagination(self, mock_libraires_api_response, app):
            # Given
            mock_libraires_api_response.side_effect = [
                iter([{
                    "ref": "9780199536986",
                    "available": 4,
                    "price": 16
                }]),
                iter([{
                    "ref": "1550199555555",
                    "available": 5,
                    "price": 14
                }])
            ]

            offerer = create_offerer()
            venue = create_venue(offerer, siret='12345678912345')

            libraires_stocks_provider = activate_provider('LibrairesStocks')
            venue_provider = create_venue_provider(venue, libraires_stocks_provider, is_active=True,
                                                   venue_id_at_offer_provider='12345678912345')
            product_1 = create_product_with_thing_type(id_at_providers='9780199536986')
            product_2 = create_product_with_thing_type(id_at_providers='1550199555555')

            repository.save(product_1, product_2, venue_provider)
            libraires_stocks = LibrairesStocks(venue_provider)

            # When
            libraires_stocks.updateObjects()

            # Then
            offers = Offer.query.all()
            stocks = StockSQLEntity.query.all()
            assert len(stocks) == 2
            assert len(offers) == 2
            assert mock_libraires_api_response.call_args_list == [call('12345678912345', '', ''),
                                                                  call('12345678912345', '9780199536986', ''),
                                                                  call('12345678912345', '1550199555555', '')]
