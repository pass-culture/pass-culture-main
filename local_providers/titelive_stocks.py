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


def get_data(after_isbn_id, last_date_checked, is_mock, venue_siret):
    if is_mock:
        # TODO:
        pass
    else:
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

        # TODO: for test purpose
        self.siret = '77567146400110'

        self.is_mock = 'mock' in options and options['mock']
        self.seen_isbn = []
        self.last_seen_isbn = 0
        self.index = -1
        self.more_pages = True
        self.data = None

    def __next__(self):
        self.index = self.index + 1

        if self.data is None \
            or len(self.data['stocks']) <= self.index:

            if not self.more_pages:
                raise StopIteration

            self.index = 0

            self.data = get_data(self.last_seen_isbn,
                                 datetime.utcfromtimestamp(1539349960),
                                 self.is_mock,
                                 # self.venueProvider.venueIdAtOfferProvider)
                                 self.siret)

            # total_objects = self.data['offset']+self.data['limit']
            # TODO: why total is null from API?
            total_objects = 200
            if self.data['total'] is None:
                total = 200
            else:
                total = self.data['total']
            self.more_pages = total_objects < total

        # print("LEN", len(self.data['stocks']))
        # print("INDEX", self.index)
        self.oa_stock = self.data['stocks'][self.index]

        self.seen_isbn.append(str(self.oa_stock['ref']))
        # self.last_seen_isbn = self.oa_stock['ref']

        thing = Thing.query.filter((Thing.type == ThingType.LIVRE_EDITION.name) &
                                   (Thing.idAtProviders == self.oa_stock['ref'])) \
            .one_or_none()

        offer_count = Offer.query.filter_by(thing=thing) \
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
        print("OBJ: ", obj)
        if isinstance(obj, Stock):
            print("TOTO")
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
