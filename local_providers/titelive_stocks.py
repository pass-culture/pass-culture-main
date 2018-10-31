import requests
from datetime import datetime

from models import ThingType
from models.local_provider import LocalProvider, ProvidableInfo
from models.offer import Offer
from models.stock import Stock
from models.thing import Thing
from models.venue import Venue

DATE_FORMAT = "%d/%m/%Y"
DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
URL_TITELIVE_WS_STOCKS = "https://stock.epagine.fr/stocks/"


def make_url(after_isbn_id, last_date_checked, venue_siret):
    if after_isbn_id:
        return 'https://stock.epagine.fr/stocks/' \
           + str(venue_siret) \
           + '?after='+str(after_isbn_id) \
           + '&modifiedSince='+str(last_date_checked)
           # + '&limit=100'
    else:
        return 'https://stock.epagine.fr/stocks/' \
               + str(venue_siret) \
               + '?modifiedSince='+str(last_date_checked)


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
        self.venue = Venue.query \
            .filter_by(id=self.venueProvider.venueId) \
            .first()
        assert self.venue is not None
        self.venueId = self.venueProvider.venueId
        self.venue_has_offer = False

        offer_count = Offer.query \
            .filter_by(venueId=self.venueId) \
            .filter(Offer.thing is not None) \
            .count()

        print("Offer count: ", str(offer_count))
        if offer_count > 0:
            self.venue_has_offer = True

        self.is_mock = 'mock' in options and options['mock']
        latest_local_provider_event = self.latestSyncStartEvent()
        if latest_local_provider_event is None:
            self.last_ws_requests = datetime.utcfromtimestamp(0).timestamp() * 1000
        else:
            self.last_ws_requests = latest_local_provider_event.date.timestamp() * 1000
        self.seen_isbn = []
        self.last_seen_isbn = ''
        self.index = -1
        self.more_pages = True
        self.data = None

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

            # Structure probably not found
            if self.data is None:
                raise StopIteration

            print("LEN", len(self.data['stocks']))
            if len(self.data['stocks']) < 5000:
                self.more_pages = False

        # print("LEN", len(self.data['stocks']))
        # print("INDEX", self.index)
        self.oa_stock = self.data['stocks'][self.index]

        self.seen_isbn.append(str(self.oa_stock['ref']))
        self.last_seen_isbn = str(self.oa_stock['ref'])

        thing = Thing.query.filter((Thing.type == ThingType.LIVRE_EDITION.name) &
                                   (Thing.idAtProviders == self.oa_stock['ref'])) \
            .one_or_none()

        offer_count = Offer.query.filter_by(thing=thing) \
            .filter_by(venueId=self.venueId) \
            .count()

        if thing is None or offer_count == 0:
            # print("   No such thing : Book:"+str(self.oa_stock['ref']) + ", or no offer associated.")
            return None

        p_info_stock = ProvidableInfo()
        p_info_stock.type = Stock
        p_info_stock.idAtProviders = str(self.oa_stock['ref'])
        p_info_stock.dateModifiedAtProvider = datetime.utcnow()

        return p_info_stock


    def updateObject(self, obj):
        assert obj.idAtProviders == str(self.oa_stock['ref'])
        if isinstance(obj, Stock):
            print("Create stock for thing: ", str(self.oa_stock['ref']))
            obj.price = int(self.oa_stock['price'])
            obj.available = int(self.oa_stock['available'])
            obj.bookingLimitDatetime = read_datetime(self.oa_stock['validUntil'])
            thing = Thing.query \
                .filter_by(idAtProviders=self.oa_stock['ref']) \
                .first()
            offer = Offer.query \
                .filter_by(thing=thing) \
                .first()
            obj.offer = offer

    def updateObjects(self, limit=None):
        super().updateObjects(limit)
