""" spreadsheet exp venues """
from datetime import datetime
from pathlib import Path
from os import path
from flask import current_app as app
from pandas import read_csv


DATE_FORMAT = "%d/%m/%Y %Hh%M"


def read_date(date):
    return datetime.strptime(date.lower(), DATE_FORMAT)


def is_filled(info):
    info = str(info)
    return info != 'nan' and info.replace(' ', '') != ''


Venue = app.model.Venue
Offerer = app.model.Offerer


class SpreadsheetExpVenues(app.model.LocalProvider):
    help = "Pas d'aide pour le moment"
    identifierDescription = "Pas d'identifiant nécessaire"\
                            + "(on synchronise tout)"
    identifierRegexp = None
    isActive = True
    name = "Experimentation Spreadsheet (Lieux)"
    objectType = Venue
    canCreate = True

    def __init__(self, offerer, mock=False):
        super().__init__(offerer)
        if mock:
            self.df = read_csv(Path(path.dirname(path.realpath(__file__))) / '..' / 'mock' / 'spreadsheet_exp' / 'Lieux.csv')
        else:
            self.df = read_csv('https://docs.google.com/spreadsheets/d/1Lj53_cgWDyQ1BqUeVtq059nXxOULL28mDmm_3p2ldpo/gviz/tq?tqx=out:csv&sheet=Lieux')
        self.lines = self.df.iterrows()
        self.mock = mock

    def __next__(self):
        self.line = self.lines.__next__()[1]

        for field in ['Date MAJ', 'Email contact', 'Latitude', 'Longitude', 'Nom', 'Adresse', 'Ref Lieu', 'Département']:
            while not is_filled(self.line[field]):
                print(field+' is empty, skipping line')
                self.__next__()

        while '@' not in self.line['Email contact']:
            print('Invalid email in "Email contact" column, skipping line')
            self.__next__()

        p_info_offerer = app.model.ProvidableInfo()
        p_info_offerer.type = Offerer
        p_info_offerer.idAtProviders = str(self.line['Ref Lieu'])
        p_info_offerer.dateModifiedAtProvider = read_date(self.line['Date MAJ'])

        p_info_venue = app.model.ProvidableInfo()
        p_info_venue.type = Venue
        p_info_venue.idAtProviders = str(self.line['Ref Lieu'])
        p_info_venue.dateModifiedAtProvider = read_date(self.line['Date MAJ'])

        return p_info_offerer, p_info_venue

    def updateObject(self, obj):
        assert obj.idAtProviders == str(self.line['Ref Lieu'])

        obj.name = self.line['Nom']
        obj.address = self.line['Adresse']

        if isinstance(obj, Venue):
            obj.latitude = self.line['Latitude']
            obj.longitude = self.line['Longitude']
            obj.managingOfferer = self.providables[0]
            obj.departementCode = str(int(self.line['Département']))
        else:
            obj.bookingEmail = self.line['Email contact'].replace('mailto:', '')


    def getDeactivatedObjectIds(self):
        return []

    def getObjectThumb(self, obj, index):
        assert obj.idAtProviders == str(self.line['Ref Lieu'])
        if self.line['Lien Image']:
            return self.line['Lien Image']
        else:
            raise ValueError('Unexpected Lien Image '
                             + obj.__class__.__name__)

    def getObjectThumbDates(self, obj):
        if self.mock:
            return []
        if is_filled(self.line['Lien Image']) != '':
            return [read_date(self.line['Date MAJ'])]


app.local_providers.SpreadsheetExpVenues = SpreadsheetExpVenues
