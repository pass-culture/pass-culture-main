from infrastructure.container import api_titelive_stocks
from local_providers.generic_provider.generic_stocks import GenericStocks
from models import VenueProvider


class TiteLiveStocks(GenericStocks):
    name = "TiteLive Stocks (Epagine / Place des libraires.com)"
    can_create = True

    def __init__(self, venue_provider: VenueProvider, **options):
        super().__init__(venue_provider=venue_provider,
                         get_provider_stock_information=api_titelive_stocks.stocks_information,
                         price_divider_to_euro=100,
                         **options)
        self.venue = venue_provider.venue
        self.siret = self.venue.siret
        self.last_processed_isbn = ''
        self.stock_data = iter([])
        self.modified_since = venue_provider.lastSyncDate
        self.product = None
        self.offer_id = None
