from models.mediation import Mediation
import re
from datetime import datetime
from os import path
from pathlib import Path

from flask import current_app as app
from pandas import read_csv

from models.local_provider import LocalProvider
from models.mediation import Mediation
from models.offer import Offer
from models.offerer import Offerer
from models.provider import Provider
from models.thing import Thing
from models.venue import Venue

DATE_FORMAT = "%d/%m/%Y %Hh%M"
HOUR_REGEX = re.compile(r"(\d)h(\d?)$", re.IGNORECASE)


def read_date(date):
    return datetime.strptime(date, DATE_FORMAT)


def is_filled(info):
    info = str(info)
    return info != 'nan' and info.replace(' ', '') != ''


Mediation = Mediation
Offer = Offer
Thing = Thing
ThingType = ThingType


class SpreadsheetExpThingOffers(LocalProvider):
    help = "Pas d'aide pour le moment"
    identifierDescription = "Pas d'identifiant nécessaire"\
                            + "(on synchronise tout)"
    identifierRegexp = None
    name = "Experimentation Spreadsheet (Offres 'Things')"
    objectType = Offer
    canCreate = True

    def __init__(self, offerer, mock=False):
        super().__init__(offerer)
        if mock:
            self.df = read_csv(Path(path.dirname(path.realpath(__file__))) / '..' / 'mock' / 'spreadsheet_exp' / 'Objets.csv')
        else:
            self.df = read_csv('https://docs.google.com/spreadsheets/d/1Lj53_cgWDyQ1BqUeVtq059nXxOULL28mDmm_3p2ldpo/gviz/tq?tqx=out:csv&sheet=Objets')
        self.lines = self.df.iterrows()
        self.mock = mock

    def __next__(self):
        self.line = self.lines.__next__()[1]

        for field in ['Ref Objet', 'Ref Lieu', 'Titre', 'Auteur', 'Type', 'Stock', 'Lien Image Accroche', 'Description', 'Date MAJ']:
            while not is_filled(self.line[field]):
                print(field+' is empty, skipping line')
                self.__next__()

        venueIdAtProviders = str(int(self.line['Ref Lieu']))

        self.venue = Venue.query\
                                    .filter_by(idAtProviders=venueIdAtProviders)\
                                    .one_or_none()

        if self.venue is None:
            print('Venue #' + venueIdAtProviders
                  + ' not found, skipping line')
            self.__next__()

        self.offerer = Offerer.query\
                                        .filter_by(idAtProviders=venueIdAtProviders)\
                                        .one_or_none()

        if self.offerer is None:
            print('Offerer #' + venueIdAtProviders
                  + ' not found, skipping line')
            self.__next__()

        self.thing = None

        providables = []

        p_info_thing = ProvidableInfo()
        p_info_thing.type = Thing
        p_info_thing.idAtProviders = str(self.line['Ref Objet'])
        p_info_thing.dateModifiedAtProvider = read_date(self.line['Date MAJ'])

        providables.append(p_info_thing)

        p_info_offer = ProvidableInfo()
        p_info_offer.type = Offer
        p_info_offer.idAtProviders = str(self.line['Ref Objet'])
        p_info_offer.dateModifiedAtProvider = read_date(self.line['Date MAJ'])

        providables.append(p_info_offer)

        if is_filled(self.line['Lien Image Accroche']) or\
           is_filled(self.line['Texte Accroche']):
            p_info_med = ProvidableInfo()
            p_info_med.type = Mediation
            p_info_med.idAtProviders = str(self.line['Ref Objet'])
            p_info_med.dateModifiedAtProvider = read_date(self.line['Date MAJ'])

            providables.append(p_info_med)

        return providables

    def updateObject(self, obj):
        if not isinstance(obj, Thing) and self.thing is None:
            self.thing = Thing.query.filter_by(idAtProviders=obj.idAtProviders, lastProviderId=Provider.getByClassName(self.__class__.__name__).id).first()
        if isinstance(obj, Thing):
            obj.name = self.line['Titre']
            obj.extraData = {'author': self.line['Auteur']}
            obj.description = self.line['Description']
            obj.mediaUrls = [self.line['Lien Internet']]
            obj.type = ThingType[self.line['Type']]
            self.thing = obj
        elif isinstance(obj, Offer):
            obj.thing = self.thing
            obj.price = 0
            obj.offerer = self.offerer
            obj.venue = self.venue
            obj.available = int(self.line['Stock'])
        elif isinstance(obj, Mediation):
            obj.thing = self.thing
            obj.offerer = self.offerer
            if is_filled(self.line['Texte Accroche']):
                obj.text = str(self.line['Texte Accroche'])

        else:
            raise ValueError('Unexpected object class in updateObj '
                             + obj.__class__.__name__)

    def getDeactivatedObjectIds(self):
        # TODO !
        return []

    def getObjectThumb(self, obj, index):
        assert obj.idAtProviders == str(self.line['Ref Objet'])
        thumb_url = None
        if isinstance(obj, Mediation):
            thumb_url = self.line['Lien Image Accroche']
        elif isinstance(obj, Thing):
            thumb_url = self.line['Lien Image']
        else:
            raise ValueError('Unexpected object class in updateObj '
                             + obj.__class__.__name__)
        return thumb_url

    def getObjectThumbDates(self, obj):
        if self.mock:
            return []
        if (isinstance(obj, Thing) and is_filled(self.line.get('Lien Image'))) or\
           (isinstance(obj, Mediation) and is_filled(self.line.get('Lien Image Accroche'))):
            return [read_date(str(self.line['Date MAJ']))]
        else:
            return []


app.local_providers.SpreadsheetExpThingOffers = SpreadsheetExpThingOffers
