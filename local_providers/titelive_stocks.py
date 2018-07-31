import os
import re
from datetime import datetime
from pathlib import Path
from zipfile import ZipFile
import pandas as pd
from flask import current_app as app

from models.local_provider import LocalProvider, ProvidableInfo
from models.offer import Offer
from models.stock import Stock
from models.thing import Thing
from models.venue import Venue

DATE_FORMAT = "%d/%m/%Y"
DATETIME_FORMAT = "%d/%m/%Y %H:%M:%S"


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
                            / '..' / 'mock' / 'providers' / 'titelive_stocks'
        else:
            data_root_path = Path(os.path.dirname(os.path.realpath(__file__)))\
                            / '..' / 'ftp_mirrors' / 'titelive_stocks'
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

    def open_next_file(self):
        f = self.stock_files.__next__()
        print("  Importing from file "+str(f.filename))
        lines = pd.read_csv(self.zip.open(f),
                            header=None,
                            delimiter=";",
                            encoding='iso-8859-1')\
                  .values
        self.data_lines = iter(lines)

    def __next__(self):

        if self.data_lines is None:
            self.open_next_file()

        isRightVenue = False
        while not isRightVenue:
            try:
                line = self.data_lines.__next__()
            except StopIteration:
                self.open_next_file()
                line = self.data_lines.__next__()
            isRightVenue = str(line[1]) == self.venueProvider.venueIdAtOfferProvider

        thing = Thing.query.filter((Thing.type == "Book") &
                                   (Thing.idAtProviders == str(line[2])))\
                           .one_or_none()

        if thing is None:
            print("   No such thing : Book:"+str(line[2]))
            return None
        self.thing = thing

        self.venue = Venue.query\
                                    .filter_by(idAtProviders=str(line[1]))\
                                    .one_or_none()

        if self.venue is None:
            print("   No such venue : "+str(line[1]))
            return None
        self.thing = thing

        if 'prix_livre' not in thing.extraData:
            print("   No extraData['prix_livre'] for Book:"+str(line[2]))
            return None

        if not thing.extraData['prix_livre']\
                    .replace('.', '', 1)\
                    .isdigit():
            print("   extraData['prix_livre'] is not a floating point number"
                  + " for Book:"+str(line[2]))
            return None

        self.price = thing.extraData['prix_livre']

        p_info_offer = ProvidableInfo()
        p_info_offer.type = Offer
        self.idAtProviders = str(line[1])+':'+str(line[2])
        p_info_offer.idAtProviders = self.idAtProviders
        p_info_offer.dateModifiedAtProvider = self.dateModified

        p_info_stock = ProvidableInfo()
        p_info_stock.type = Stock
        self.idAtProviders = str(line[1])+':'+str(line[2])
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


app.local_providers.TiteLiveStocks = TiteLiveStocks
