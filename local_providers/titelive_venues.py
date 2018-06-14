from datetime import datetime
from flask import current_app as app
import luhn
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
    name = "TiteLive Venues (Epagine / Place des libraires.com)"
    objectType = Venue
    canCreate = True

    def __init__(self, venueProvider, **options):
        super().__init__(venueProvider, **options)
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

        p_info_venueProvider = app.model.ProvidableInfo()
        p_info_venueProvider.type = app.model.VenueProvider
        p_info_venueProvider.idAtProviders = str(row[0])
        p_info_venueProvider.dateModifiedAtProvider = self.dateModified

        return p_info_offerer, p_info_venue, p_info_venueProvider

    def updateObject(self, obj):
        row = self.row

        assert obj.idAtProviders == str(row[0])

        if isinstance(obj, app.model.Venue):
            obj.latitude = row[7]
            obj.longitude = row[8]
            obj.departementCode = str(row[4]).strip()[:2]
            obj.name = row[2]
            obj.address = row[3]
            obj.postalCode = str(row[4]).strip()
            obj.city = row[5]
            obj.managingOfferer = self.providables[0]
            obj.siret = luhn.append(str(row[1]))
        elif isinstance(obj, app.model.Offerer):
            obj.bookingEmail = 'passculture-dev@beta.gouv.fr'
            obj.name = row[2]
            obj.address = row[3]
            obj.postalCode = str(row[4]).strip()
            obj.city = row[5]
            obj.siren = str(row[1])[:9]
        elif isinstance(obj, app.model.VenueProvider):
            obj.provider = self.titelive_offer_provider
            obj.venue = self.providables[1]
            obj.venueIdAtOfferProvider = str(row[0])
            obj.isActive = False
        else:
            raise ValueError('Unexpected object class in updateObj '
                             + obj.__class__.__name__)


app.local_providers.TiteLiveVenues = TiteLiveVenues
