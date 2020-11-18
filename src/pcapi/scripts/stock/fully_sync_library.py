from pcapi.core.bookings.repository import count_not_cancelled_bookings_quantity_by_stock_id
from pcapi.core.offers.models import Offer
from pcapi.local_providers.venue_provider_worker import do_sync_venue_provider
from pcapi.models import Stock
from pcapi.models import VenueProvider
from pcapi.repository import repository


STOCK_BATCH_UPDATE = 100


def fully_sync_library(venue_id: int) -> None:
    stocks = Stock.query.join(Offer).filter(Offer.venueId == venue_id).filter(Offer.idAtProviders != None).all()

    stocks_to_update = []
    for stock in stocks:
        stock.quantity = count_not_cancelled_bookings_quantity_by_stock_id(stock.id)
        stocks_to_update.append(stock)
        if len(stocks_to_update) >= STOCK_BATCH_UPDATE:
            repository.save(*stocks_to_update)
            stocks_to_update = []

    repository.save(*stocks_to_update)

    venue_provider_to_sync = VenueProvider.query.filter(VenueProvider.venueId == venue_id).one()
    venue_provider_to_sync.lastSyncDate = None
    repository.save(venue_provider_to_sync)

    do_sync_venue_provider(venue_provider_to_sync)
