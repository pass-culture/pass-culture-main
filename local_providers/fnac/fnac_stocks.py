from infrastructure.container import api_fnac_stocks
from local_providers.generic_provider.generic_stocks import GenericStocks
from models import VenueProvider


class FnacStocks(GenericStocks):
    name = 'FNAC'
    can_create = True

    def __init__(self, venue_provider: VenueProvider, **options):
        super().__init__(venue_provider,
                         api_fnac_stocks.stocks_information,
                         **options)
        self.venue = venue_provider.venue
        self.siret = self.venue.siret
        self.last_processed_isbn = ''
        self.stock_data = iter([])
        self.modified_since = venue_provider.lastSyncDate
        self.product = None
        self.offer_id = None
