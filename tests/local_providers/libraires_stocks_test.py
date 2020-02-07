from unittest.mock import patch

from local_providers.libraires_stocks import LibrairesStocks
from models import Offer, Stock
from repository import repository
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_venue_provider, create_venue, create_offerer, create_stock
from tests.model_creators.provider_creators import activate_provider
from tests.model_creators.specific_creators import create_product_with_thing_type, create_offer_with_thing_product


class LibrairesStocksTest:
    class InitTest:
        @clean_database
        @patch('local_providers.libraires_stocks.get_libraires_stock_information')
        def test_should_call_libraires_api(self, mock_libraires_api_response, app):
            # Given
            last_processed_isbn = ''
            modified_since = ''
            offerer = create_offerer()
            venue = create_venue(offerer, siret='12345678912345')
            libraires_provider = activate_provider('LibrairesStocks')
            venue_provider = create_venue_provider(venue, libraires_provider)

            repository.save(venue_provider)

            # When
            LibrairesStocks(venue_provider)

            # Then
            mock_libraires_api_response.assert_called_once_with(venue.siret, last_processed_isbn, modified_since)

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
            assert len(libraires_providable_infos) == 2

            offer_providable_info = libraires_providable_infos[0]
            stock_providable_info = libraires_providable_infos[1]

            assert offer_providable_info.type == Offer
            assert offer_providable_info.id_at_providers == '9780199536986@12345678912345'
            assert stock_providable_info.type == Stock
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
            stock = Stock.query.first()

            assert offer.type == product.type
            assert offer.description == product.description
            assert offer.venue is not None
            assert offer.bookingEmail == venue.bookingEmail
            assert offer.extraData == product.extraData

            assert stock.price == 16.5
            assert stock.available == 10
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
            stock = create_stock(offer=offer, id_at_providers='9780199536986@12345678912345', available=20)

            repository.save(product, offer, stock)
            libraires_stocks = LibrairesStocks(venue_provider)

            # When
            libraires_stocks.updateObjects()

            # Then
            stock = Stock.query.one()
            assert stock.available == 10
            assert Offer.query.count() == 1

        @clean_database
        @patch('local_providers.libraires_stocks.get_libraires_stock_information')
        def test_libraires_stock_provider_deactivate_offer_if_stock_available_equals_0(self,
                                                                                       mock_libraires_api_response,
                                                                                       app):
            # Given
            mock_libraires_api_response.return_value = iter([{
                "ref": "9780199536986",
                "available": 0,
                "price": 16
            }])

            offerer = create_offerer()
            venue = create_venue(offerer, siret='12345678912345')

            libraires_stocks_provider = activate_provider('LibrairesStocks')
            venue_provider = create_venue_provider(venue, libraires_stocks_provider, is_active=True,
                                                   venue_id_at_offer_provider='12345678912345')
            product = create_product_with_thing_type(id_at_providers='9780199536986')

            offer = create_offer_with_thing_product(venue, product=product,
                                                    id_at_providers='9780199536986@12345678912345')
            stock = create_stock(offer=offer, id_at_providers='9780199536986@12345678912345')
            repository.save(product, venue_provider, stock)

            libraires_stocks = LibrairesStocks(venue_provider)

            # When
            libraires_stocks.updateObjects()

            # Then
            offer = Offer.query.one()
            assert offer.isActive is False

        @clean_database
        @patch('local_providers.libraires_stocks.get_libraires_stock_information')
        def test_libraires_stock_provider_reactivate_offer_if_new_stocks_are_available(self,
                                                                                       mock_libraires_api_response,
                                                                                       app):
            # Given
            mock_libraires_api_response.side_effect = [iter([{
                "ref": "9780199536986",
                "available": 20,
                "price": 17
            }])
            ]

            offerer = create_offerer()
            venue = create_venue(offerer, siret='12345678912345')

            libraires_stocks_provider = activate_provider('LibrairesStocks')
            venue_provider = create_venue_provider(venue, libraires_stocks_provider, is_active=True,
                                                   venue_id_at_offer_provider='12345678912345')
            product = create_product_with_thing_type(id_at_providers='9780199536986')

            offer = create_offer_with_thing_product(venue, product=product, is_active=False,
                                                    id_at_providers='9780199536986@12345678912345')
            stock = create_stock(offer=offer, id_at_providers='9780199536986@12345678912345', available=0)
            repository.save(offer, stock, product, venue_provider, libraires_stocks_provider)

            libraires_stocks = LibrairesStocks(venue_provider)

            # When
            libraires_stocks.updateObjects()

            # Then
            offer = Offer.query.one()
            assert offer.isActive

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
            offer = create_offer_with_thing_product(venue, product=product_2, id_at_providers='everything_but_libraires')

            repository.save(offer, product_1, product_2, venue_provider)

            libraires_stocks = LibrairesStocks(venue_provider)

            # When
            libraires_stocks.updateObjects()

            # Then
            assert Stock.query.count() == 2
            assert Offer.query.filter_by(lastProviderId=libraires_stocks_provider.id).count() == 2
            assert libraires_stocks.last_processed_isbn == '1550199555555'

    class WhenSynchronizedTwiceTest:
        @clean_database
        @patch('local_providers.libraires_stocks.get_libraires_stock_information')
        def test_should_update_stocks_after_second_synchronisation(self, mock_libraires_api_response, app):
            # Given
            mock_libraires_api_response.side_effect = [
                iter([{
                    "ref": "9780199536986",
                    "available": 4,
                    "price": 16
                },
                    {"ref": "1550199555555",
                     "available": 3,
                     "price": 15
                     }]),
                iter([{
                    "ref": "9780199536986",
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
            libraires_stocks.updateObjects()

            # When
            libraires_stocks = LibrairesStocks(venue_provider)
            libraires_stocks.updateObjects()

            # Then
            offers = Offer.query.all()
            stocks = Stock.query.all()
            assert len(stocks) == 2
            assert len(offers) == 2

            first_stock = stocks[0]
            second_stock = stocks[1]

            assert first_stock.idAtProviders == '1550199555555@12345678912345'
            assert first_stock.available == 3
            assert second_stock.idAtProviders == '9780199536986@12345678912345'
            assert second_stock.available == 5
