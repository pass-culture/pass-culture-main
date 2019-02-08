import requests
from datetime import datetime

from models import Offer
from models.db import db
from models.local_provider import LocalProvider, ProvidableInfo
from models.stock import Stock
from repository import thing_queries, local_provider_event_queries, venue_queries
from utils.ftp_titelive import read_stock_datetime
from utils.logger import logger

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

    def __init__(self, venueProvider, **options):
        super().__init__(venueProvider, **options)
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
        self.thing = None

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

        self.thing = thing_queries.find_thing_by_isbn_only_for_type_book(self.titelive_stock['ref'])

        if self.thing is None:
            return self.__next__()

        # Refresh data before using it
        db.session.add(self.venue)

        p_info_stock = ProvidableInfo()
        p_info_stock.type = Stock
        p_info_stock.idAtProviders = "%s@%s" % (self.titelive_stock['ref'], self.venue.siret)
        p_info_stock.dateModifiedAtProvider = datetime.utcnow()

        p_info_offer = ProvidableInfo()
        p_info_offer.type = Offer
        p_info_offer.idAtProviders = "%s@%s" % (self.titelive_stock['ref'], self.venue.siret)
        p_info_offer.dateModifiedAtProvider = datetime.utcnow()

        return p_info_offer, p_info_stock

    def updateObject(self, obj):
        assert obj.idAtProviders == "%s@%s" % (self.titelive_stock['ref'], self.venue.siret)
        if isinstance(obj, Stock):
            logger.info("Create stock for thing: %s" % self.titelive_stock['ref'])
            obj.price = int(self.titelive_stock['price'])
            obj.available = int(self.titelive_stock['available'])
            obj.bookingLimitDatetime = read_stock_datetime(self.titelive_stock['validUntil'])
            obj.offer = self.providables[0]
        elif isinstance(obj, Offer):
            obj.venue = self.venue
            obj.thing = self.thing


    def updateObjects(self, limit=None):
        super().updateObjects(limit)
