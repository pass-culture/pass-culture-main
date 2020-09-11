from unittest.mock import patch, call

from local_providers.fnac.fnac_stocks import FnacStocks
from models import OfferSQLEntity, StockSQLEntity
from repository import repository
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_venue_provider, create_venue, create_offerer
from tests.model_creators.provider_creators import activate_provider
from tests.model_creators.specific_creators import create_product_with_thing_type


class FnacStocksTest:
    class NextTest:
        @clean_database
        @patch('local_providers.fnac.fnac_stocks.get_fnac_stock_information')
        def test_should_return_providable_infos_with_correct_data(self, mock_fnac_api_response, app):
            # Given
            mock_fnac_api_response.return_value = iter([
                {
                    "Ref": "9780199536986",
                    "Available": 1,
                    "Price": 6.36
                }
            ])

            offerer = create_offerer()
            venue = create_venue(offerer, siret='12345678912345')
            fnac_provider = activate_provider('FnacStocks')
            venue_provider = create_venue_provider(venue, fnac_provider, venue_id_at_offer_provider=venue.siret)
            product = create_product_with_thing_type(id_at_providers='9780199536986')

            repository.save(venue_provider, product)

            fnac_stocks_provider = FnacStocks(venue_provider)

            # When
            fnac_providable_infos = next(fnac_stocks_provider)

            # Then
            assert mock_fnac_api_response.call_args_list == [call('12345678912345', '', '')]
            assert len(fnac_providable_infos) == 2

            offer_providable_info = fnac_providable_infos[0]
            stock_providable_info = fnac_providable_infos[1]

            assert offer_providable_info.type == OfferSQLEntity
            assert offer_providable_info.id_at_providers == '9780199536986@12345678912345'
            assert stock_providable_info.type == StockSQLEntity
            assert stock_providable_info.id_at_providers == '9780199536986@12345678912345'
