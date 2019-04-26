import requests
from datetime import datetime

from domain.titelive import read_stock_datetime
from models import Offer, VenueProvider, PcObject
from models.db import db
from models.local_provider import LocalProvider, ProvidableInfo
from models.stock import Stock
from repository import thing_queries, local_provider_event_queries, venue_queries
from repository.offer_queries import find_offer_by_id_at_providers

URL_TITELIVE_WEBSERVICE_STOCKS = "https://stock.epagine.fr/stocks/"
NB_DATA_LIMIT_PER_REQUEST = 5000


def make_url(last_seen_isbn, last_date_checked, venue_siret):
    if last_seen_isbn:
        return 'https://stock.epagine.fr/stocks/%s?after=%s&modifiedSince=%s' \
               % (venue_siret, last_seen_isbn, last_date_checked)
    else:
        return 'https://stock.epagine.fr/stocks/%s?modifiedSince=%s' \
               % (venue_siret, last_date_checked)


def get_data(last_seen_isbn, last_date_checked, venue_siret):
    page_url = make_url(last_seen_isbn, last_date_checked, venue_siret)
    req_result = requests.get(page_url)
    return req_result.json()


class TiteLiveStocks(LocalProvider):
    help = ""
    identifierDescription = "Code Titelive de la librairie"
    identifierRegexp = "^\d+$"
    name = "TiteLive Stocks (Epagine / Place des libraires.com)"
    objectType = Stock
    canCreate = True

    def __init__(self, venue_provider: VenueProvider, **options):
        super().__init__(venue_provider, **options)
        self.venueId = self.venueProvider.venueId
        self.venue = venue_queries.find_by_id(self.venueId)
        assert self.venue is not None

        latest_local_provider_event = local_provider_event_queries.find_latest_sync_start_event(self.dbObject)
        if latest_local_provider_event is None:
            self.last_ws_requests = datetime.utcfromtimestamp(0).timestamp() * 1000
        else:
            self.last_ws_requests = latest_local_provider_event.date.timestamp() * 1000
        self.last_seen_isbn = ''
        self.index = -1
        self.more_pages = True
        self.data = None
        self.product = None
        self.existing_offer = None

    def __next__(self):
        self.index = self.index + 1

        if self.data is None \
                or len(self.data['stocks']) <= self.index:

            if not self.more_pages:
                raise StopIteration

            self.index = 0

            self.data = get_data(self.last_seen_isbn,
                                 self.last_ws_requests,
                                 self.venueProvider.venueIdAtOfferProvider)

            if 'status' in self.data \
                    and self.data['status'] == 404:
                raise StopIteration

            if len(self.data['stocks']) < NB_DATA_LIMIT_PER_REQUEST:
                self.more_pages = False

        self.titelive_stock = self.data['stocks'][self.index]
        self.last_seen_isbn = str(self.titelive_stock['ref'])

        self.product = thing_queries.find_thing_product_by_isbn_only_for_type_book(self.titelive_stock['ref'])

        if self.product is None:
            return next(self)

        # Refresh data before using it
        db.session.add(self.venue)

        providable_info_stock = ProvidableInfo()
        providable_info_stock.type = Stock
        providable_info_stock.idAtProviders = "%s@%s" % (self.titelive_stock['ref'], self.venue.siret)
        providable_info_stock.dateModifiedAtProvider = datetime.utcnow()

        self.existing_offer = find_offer_by_id_at_providers("%s@%s" % (self.titelive_stock['ref'], self.venue.siret))

        self.existing_offer = Offer.query \
            .filter_by(idAtProviders="%s@%s" % (self.titelive_stock['ref'], self.venue.siret)) \
            .one_or_none()

        if self.existing_offer is None:
            providable_info_offer = ProvidableInfo()
            providable_info_offer.type = Offer
            providable_info_offer.idAtProviders = "%s@%s" % (self.titelive_stock['ref'], self.venue.siret)
            providable_info_offer.dateModifiedAtProvider = datetime.utcnow()
        else:
            providable_info_offer = None

        return providable_info_offer, providable_info_stock

    def updateObject(self, obj):
        assert obj.idAtProviders == "%s@%s" % (self.titelive_stock['ref'], self.venue.siret)
        if isinstance(obj, Stock):
            self.update_stock_object(obj, self.titelive_stock, self.existing_offer)
        elif isinstance(obj, Offer) \
                and self.existing_offer is None:
            self.update_offer_object(obj)

    def updateObjects(self, limit=None):
        super().updateObjects(limit)

    def update_stock_object(self, obj, stock_information, offer):
        obj.price = int(stock_information['price'])
        obj.available = int(stock_information['available'])
        obj.bookingLimitDatetime = read_stock_datetime(stock_information['validUntil'])
        if offer:
            obj.offerId = offer.id
        else:
            providable_offer = self.providables[0]
            obj.offerId = providable_offer.id

    def update_offer_object(self, obj):
        obj.name = self.product.name
        obj.venueId = self.venueId
        obj.productId = self.product.id
        PcObject.check_and_save(obj)
