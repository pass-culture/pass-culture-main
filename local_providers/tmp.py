import json
import os
import re
from urllib.error import HTTPError
import requests
from datetime import datetime
from pathlib import Path
from zipfile import ZipFile
import pandas as pd

from models import ThingType
from models.local_provider import LocalProvider, ProvidableInfo
from models.offer import Offer
from models.stock import Stock
from models.thing import Thing
from models.venue import Venue

DATE_FORMAT = "%d/%m/%Y"
DATETIME_FORMAT = "%d/%m/%Y %H:%M:%S"
URL_TITELIVE_WS_STOCKS = "https://stock.epagine.fr/stocks/"



def make_url(date_after, id):
    return 'https://stock.epagine.fr/stocks/' \
           + str(id) \
           + '?after='+str(date_after)


def get_data(date_after, id, is_mock):
    if is_mock:
        with open(Path(os.path.dirname(os.path.realpath(__file__)))
                  / '..' / 'mock' / 'providers'
                  / ('openagenda' + str(page) + '.json')) as f:
            return json.load(f)
    else:
        page_url = make_url(date_after, id)
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
        self.is_mock = False
        if 'mock' in options and options['mock']:
            self.is_mock = True
            data_root_path = Path(os.path.dirname(os.path.realpath(__file__))) \
                             / '..' / 'mock' / 'providers' / 'titelive_stocks'
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
            print(venueProvider.venueIdAtOfferProvider)
            try:
                self.siret = int(venueProvider.venueIdAtOfferProvider)
            except ValueError:
                print('Invalid venueIdAtOfferProvider in venueProvider')
                self.siret = 77567146400110

            self.data_lines = None
            self.stock_files = None
            stock_venue_provider_url = URL_TITELIVE_WS_STOCKS + str(self.siret)
            try:
                # TODO: if total is null, we need to call another time with page parameter
                response = urlopen(stock_venue_provider_url)
                data = response.read()
                values = json.loads(data)
                self.data_lines  = values
            except HTTPError as e:
                content = e.read()
                print(content)


    def open_next_file(self):
        f = self.stock_files.__next__()
        if self.is_mock:
            print("  Importing from file "+str(f.filename))
            lines = pd.read_csv(self.zip.open(f),
                                header=None,
                                delimiter=";",
                                encoding='iso-8859-1') \
                .values
        else:
            lines = self.stock_files
        self.data_lines = iter(lines)

    def __next__(self):

        if self.data_lines is None:
            self.open_next_file()

        # isRightVenue = False
        # while not isRightVenue:
        #     try:
        #         line = self.data_lines.__next__()
        #     except StopIteration:
        #         self.open_next_file()
        #         line = self.data_lines.__next__()
        #     isRightVenue = str(line[1]) == self.venueProvider.venueIdAtOfferProvider

        for data in self.data_lines['stocks']:
            print(data['prix_livre'])
            thing = Thing.query.filter((Thing.type == ThingType.LIVRE_EDITION.name) &
                                       (Thing.idAtProviders == str(data['ref']))) \
                .one_or_none()

            if thing is None:
                print("   No such thing : Book:"+str(data['ref']))
                return None
            # self.thing = thing
            #
            # self.venue = Venue.query\
            #                             .filter_by(idAtProviders=str(line[1]))\
            #                             .one_or_none()

            # if self.venue is None:
            #     print("   No such venue : "+str(line[1]))
            #     return None
            self.thing = thing

            if 'prix_livre' not in thing.extraData:
                print("   No extraData['prix_livre'] for Book:"+str(data['ref']))
                return None

            if not thing.extraData['prix_livre'] \
                    .replace('.', '', 1) \
                    .isdigit():
                print("   extraData['prix_livre'] is not a floating point number"
                      + " for Book:"+str(data['ref']))
                return None

            self.price = thing.extraData['prix_livre']

            p_info_offer = ProvidableInfo()
            p_info_offer.type = Offer
            self.idAtProviders = str(self.siret)+':'+str(data['ref'])
            p_info_offer.idAtProviders = self.idAtProviders
            p_info_offer.dateModifiedAtProvider = self.dateModified

            p_info_stock = ProvidableInfo()
            p_info_stock.type = Stock
            self.idAtProviders = str(self.siret)+':'+str(data['ref'])
            p_info_stock.idAtProviders = self.idAtProviders
            p_info_stock.dateModifiedAtProvider = self.dateModified

            return p_info_offer, p_info_stock


    def updateObject(self, obj):
        assert obj.idAtProviders == self.idAtProviders
        if isinstance(obj, Stock):
            obj.offer = self.providables[0]
            obj.offererId = self.venue.managingOffererId
            obj.price = self.price
        else:
            obj.thing = self.thing
            obj.venue = self.venue


    def getDeactivatedObjectIds(self):
        #TODO
        return []
