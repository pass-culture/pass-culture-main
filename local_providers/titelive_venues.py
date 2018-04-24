from datetime import datetime
from flask import current_app as app
import os
import pandas as pd
from pathlib import Path
import re
from zipfile import ZipFile

Venue = app.model.Venue
Offerer = app.model.Offerer


class TiteLiveVenues(app.model.LocalProvider):

    help = ""
    identifierDescription = ""
    identifierRegexp = None
    isActive = True
    name = "TiteLive Venues (Epagine / Place des libraires.com)"
    objectType = Venue
    canCreate = True

    def __init__(self, offerer, **options):
        super().__init__(offerer, **options)
        if 'mock' in options and options['mock']:
            data_root_path = Path(os.path.dirname(os.path.realpath(__file__)))\
                            / '..' / 'mock' / 'providers' / 'titelive_offers'
        else:
            data_root_path = Path(os.path.dirname(os.path.realpath(__file__)))\
                            / '..' / 'ftp_mirrors' / 'titelive_offers'
        titelive_venues_zip = data_root_path / 'StockGroupes.zip'
        if not os.path.isfile(titelive_venues_zip):
            raise ValueError('File not found : '+str(titelive_venues_zip)
                             +'\nDid you run "pc ftp_mirrors" ?')
        with ZipFile(str(titelive_venues_zip)) as zip:
            with zip.open('magasins.csv') as f:
                lines = pd.read_csv(f,
                                    delimiter=";",
                                    encoding='iso-8859-1',
                                    header=None)\
                          .values
                self.data_lines = iter(lines)
        with open(data_root_path / "Date_export.txt", "r") as f:
            infos = f.readline()
        date_regexp = re.compile('EXTRACTION DU (.*)')
        match = date_regexp.search(infos)
        if match:
            self.dateModified = datetime.strptime(match.group(1), "%d/%m/%Y %H:%M")
        else:
            raise ValueError('Invalid Date_export.txt file format in titelive_offers')
        self.titelive_offer_provider = app.model.Provider.query\
                                        .filter_by(localClass='TiteLiveOffers')\
                                        .one_or_none()
        assert self.titelive_offer_provider is not None

    def __next__(self):

        row = self.data_lines.__next__()
        self.row = row

        p_info_venue = app.model.ProvidableInfo()
        p_info_venue.type = app.model.Venue
        p_info_venue.idAtProviders = str(row[0])
        p_info_venue.dateModifiedAtProvider = self.dateModified

        p_info_offerer = app.model.ProvidableInfo()
        p_info_offerer.type = app.model.Offerer
        p_info_offerer.idAtProviders = str(row[0])
        p_info_offerer.dateModifiedAtProvider = self.dateModified

        p_info_offererProvider = app.model.ProvidableInfo()
        p_info_offererProvider.type = app.model.OffererProvider
        p_info_offererProvider.idAtProviders = str(row[0])
        p_info_offererProvider.dateModifiedAtProvider = self.dateModified

        return p_info_venue, p_info_offerer, p_info_offererProvider

    def updateObject(self, obj):
        row = self.row

        assert obj.idAtProviders == str(row[0])

        obj.name = row[2]
        obj.address = "\n".join(map(str, row[3:6]))

        if isinstance(obj, app.model.Venue):
            obj.latitude = row[7]
            obj.longitude = row[8]
        elif isinstance(obj, app.model.Offerer):
            obj.venue = self.providables[0]
            obj.bookingEmail = 'passculture-dev@beta.gouv.fr'
        elif isinstance(obj, app.model.OffererProvider):
            obj.provider = self.titelive_offer_provider
            obj.offerer = self.providables[1]
            obj.offererIdAtOfferProvider = str(row[0])
        else:
            raise ValueError('Unexpected object class in updateObj '
                             + obj.__class__.__name__)


app.local_providers.TiteLiveVenues = TiteLiveVenues
