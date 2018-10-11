import requests
from datetime import datetime

from models import ThingType
from models.db import db
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
        if 'mock' in options and options['mock']:
            data_root_path = Path(os.path.dirname(os.path.realpath(__file__)))\
                            / '..' / 'sandboxes' / 'providers' / 'titelive_stocks'
            if not os.path.isdir(data_root_path):
                raise ValueError('File not found : '+str(data_root_path)
                                 + '\nDid you run "pc ftp_mirrors" ?')
            self.zip = ZipFile(str(data_root_path / 'StockGroupes.zip'))
            self.stock_files = iter(filter(lambda i: i.filename.startswith('association'), self.zip.infolist()))

            self.data_lines = None
            with open(data_root_path / "Date_export.txt", "r") as f:
                infos = f.readline()
            date_regexp = re.compile('EXTRACTION DU (.*)')
            match = date_regexp.search(infos)
            if match:
                self.dateModified = datetime.strptime(match.group(1), "%d/%m/%Y %H:%M")
            else:
                raise ValueError('Invalid Date_export.txt file format in titelive_stocks')
        else:
            print(venueProvider.idAtProviders)
            response = urlopen(URL_TITELIVE_WS_STOCKS + '77567146400110')
            data = response.read()
            values = json.loads(data)


    def open_next_file(self):
        f = self.stock_files.__next__()
        print("  Importing from file "+str(f.filename))
        lines = pd.read_csv(self.zip.open(f),
                            header=None,
                            delimiter=";",
                            encoding='iso-8859-1')\
                  .values
        self.data_lines = iter(lines)
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

        if self.data is None or len(self.data['stocks']) <= self.index:

            if not self.more_pages:
                raise StopIteration

            # self.page = self.page+1
            # TODO: get last_seen_isbn
            self.index = 0

            self.data = get_data(self.last_seen_isbn,
                                 datetime.utcfromtimestamp(1539349960),
                                 self.is_mock,
                                 # self.venueProvider.venueIdAtOfferProvider)
                                 self.siret)

            # total_objects = self.data['offset']+self.data['limit']
            # TODO: why total is null ?
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

        # TODO: something wrong in here
        thing = Thing.query.filter((Thing.type == ThingType.LIVRE_EDITION.name) &
                                   (Thing.idAtProviders == self.oa_stock['ref'])) \
            .one_or_none()

        if thing is None:
            # print("   No such thing : Book:"+str(self.oa_stock['ref']))
            return None

        p_info_stock = ProvidableInfo()
        p_info_stock.type = Stock
        p_info_stock.idAtProviders = str(self.oa_stock['ref'])
        p_info_stock.dateModifiedAtProvider = datetime.utcnow()

        return p_info_stock


    def updateObject(self, obj):
        print(obj)
        print(self.providables)
        assert obj.idAtProviders == str(self.oa_stock['ref'])
        if isinstance(obj, Stock) or isinstance(obj, 'thingStock'):
            obj.price = int(self.oa_stock['price'])
            print("Price: ", str(self.oa_stock['price']))
            obj.available = int(self.oa_stock['available'])
            obj.bookingLimitDatetime = read_datetime(self.oa_stock['validUntil'])
            obj.offer = self.providables[0]
            db.session.add(self.venue)
            print(self.venue.managingOffererId)
            obj.offererId = self.venue.managingOffererId
            thing = Thing.query \
                        .filter_by(idAtProviders=self.oa_stock['ref']) \
                .first()
        # elif isinstance(obj, Offer):
        #     thing = Thing.query \
        #         .filter_by(idAtProviders=self.oa_stock['ref']) \
        #         .first()
        #     print("thing")
        #     print(thing)
        #     obj.thing = thing
        #     print(self.venue)
        #     print(self.venueId)
            # obj.venue = self.venue
        # else:
        #     raise ValueError('Unexpected object class in updateObject: '
        #                      + obj.__class__.__name__)

    def updateObjects(self, limit=None):
        super().updateObjects(limit)
