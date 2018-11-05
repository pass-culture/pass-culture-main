import requests
from datetime import datetime

from models.local_provider import LocalProvider, ProvidableInfo
from models.stock import Stock
from repository import venue_queries, offer_queries, thing_queries, local_provider_event_queries
from utils.logger import logger

DATE_FORMAT = "%d/%m/%Y"
DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
URL_TITELIVE_WEBSERVICE_STOCKS = "https://stock.epagine.fr/stocks/"
NB_DATA_LIMIT_PER_REQUEST = 5000


def make_url(last_seen_isbn, last_date_checked, venue_siret):
    if last_seen_isbn:
        return 'https://stock.epagine.fr/stocks/%s?after=%s&modifiedSince=%s' \
           % (venue_siret, last_seen_isbn, last_date_checked)
    else:
        return 'https://stock.epagine.fr/stocks/%s?modifiedSince=%s' \
               % (venue_siret, last_date_checked)


def get_data(after_isbn_id, last_date_checked, venue_siret):
    page_url = make_url(after_isbn_id, last_date_checked, venue_siret)
    req_result = requests.get(page_url)
    return req_result.json()


def read_date(date):
    return datetime.strptime(date, DATE_FORMAT)


def read_datetime(date):
    return datetime.strptime(date, DATETIME_FORMAT)


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
        self.venue_has_offer = False
        offer_count = offer_queries.count_offers_for_things_only_for_venue_id(self.venueId)

        print("Offer count: ", str(offer_count))
        if offer_count > 0:
            self.venue_has_offer = True

        latest_local_provider_event = local_provider_event_queries.get_latest_sync_start_event(self.dbObject)
        if latest_local_provider_event is None:
            self.last_ws_requests = datetime.utcfromtimestamp(0).timestamp() * 1000
        else:
            self.last_ws_requests = latest_local_provider_event.date.timestamp() * 1000
        self.last_seen_isbn = ''
        self.index = -1
        self.more_pages = True
        self.data = None
        self.offer = None

    def __next__(self):
        if not self.venue_has_offer:
            raise StopIteration

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

        thing = thing_queries.find_thing_by_isbn_only_for_type_book(self.titelive_stock['ref'])
        self.offer = offer_queries.get_offer_for_venue_id_and_specific_thing(self.venueId, thing)

        if thing is None or self.offer is None:
            return None

        p_info_stock = ProvidableInfo()
        p_info_stock.type = Stock
        p_info_stock.idAtProviders = str(self.titelive_stock['ref'])
        p_info_stock.dateModifiedAtProvider = datetime.utcnow()

        return p_info_stock

    def updateObject(self, obj):
        assert obj.idAtProviders == str(self.titelive_stock['ref'])
        if isinstance(obj, Stock):
            logger.info("Create stock for thing: %s" % self.titelive_stock['ref'])
            obj.price = int(self.titelive_stock['price'])
            obj.available = int(self.titelive_stock['available'])
            obj.bookingLimitDatetime = read_datetime(self.titelive_stock['validUntil'])
            obj.offer = self.offer

    def updateObjects(self, limit=None):
        super().updateObjects(limit)
