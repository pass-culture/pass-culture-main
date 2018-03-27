from datetime import datetime
import dateparser
from flask import current_app as app
from math import floor
from os import path
from pandas import read_csv
from pathlib import Path
import re
import requests

from utils.string_processing import parse_timedelta


DATE_FORMAT = "%d/%m/%Y %Hh%M"
HOUR_REGEX = re.compile(r"(\d)h(\d?)$", re.IGNORECASE)


def read_date(date):
    return datetime.strptime(date, DATE_FORMAT)


Event = app.model.Event
EventOccurence = app.model.EventOccurence
Mediation = app.model.Mediation
Offer = app.model.Offer


class SpreadsheetExpOffers(app.model.LocalProvider):
    help = "Pas d'aide pour le moment"
    identifierDescription = "Pas d'identifiant nécessaire"\
                            + "(on synchronise tout)"
    identifierRegexp = None
    isActive = True
    name = "Experimentation Spreadsheet (Offres)"
    objectType = Offer
    canCreate = True

    def __init__(self, offerer, mock=False):
        super().__init__(offerer)
        if mock:
            self.df = read_csv(Path(path.dirname(path.realpath(__file__))) / '..' / 'mock' / 'spreadsheet_exp' / 'Evenements.csv')
        else:
            self.df = read_csv(
                #'https://docs.google.com/spreadsheets/d/1Lj53_cgWDyQ1BqUeVtq059nXxOULL28mDmm_3p2ldpo/gviz/tq?tqx=out:csv&sheet=Evenements'
                'https://docs.google.com/spreadsheets/d/1o4LXJJEcGZ2QO307CdZVOMziGXpgMr7gYyvaqVtrNOs/gviz/tq?tqx=out:csv&sheet=Evenements'
            )
        self.lines = self.df.iterrows()
        self.mock = mock

    def __next__(self):
        self.line = self.lines.__next__()[1]

        providables = []

        p_info_event = app.model.ProvidableInfo()
        p_info_event.type = Event
        p_info_event.idAtProviders = str(self.line['Ref Évènement'])
        p_info_event.dateModifiedAtProvider = read_date(self.line['Date MAJ'])

        providables.append(p_info_event)

        for index, horaire in enumerate(self.line['Horaires'].split(';')):
            horaire = HOUR_REGEX.sub(r'\1:\2', horaire)
            if horaire.endswith(':'):
                horaire = horaire + '00'
            evocc_dt = dateparser.parse(horaire, languages=['fr'])

            p_info_evocc = app.model.ProvidableInfo()
            p_info_evocc.type = EventOccurence
            p_info_evocc.idAtProviders = str(self.line['Ref Évènement']) + '_'\
                                         + evocc_dt.isoformat()
            p_info_evocc.dateModifiedAtProvider = read_date(self.line['Date MAJ'])

            providables.append(p_info_evocc)

            p_info_offer = app.model.ProvidableInfo()
            p_info_offer.type = Offer
            p_info_offer.idAtProviders = str(self.line['Ref Évènement']) + '_'\
                                         + evocc_dt.isoformat()
            p_info_offer.dateModifiedAtProvider = read_date(self.line['Date MAJ'])

            providables.append(p_info_offer)

        if str(self.line['Lien Image Accroche']).replace(' ', '') != '' or\
           str(self.line['Texte Accroche']).replace(' ', '') != '':
            p_info_med = app.model.ProvidableInfo()
            p_info_med.type = Mediation
            p_info_med.idAtProviders = str(self.line['Ref Évènement'])
            p_info_med.dateModifiedAtProvider = read_date(self.line['Date MAJ'])

            providables.append(p_info_med)

        return providables

    def updateObject(self, obj):
        if isinstance(obj, Event):
            obj.name = self.line['Titre']
            obj.description = self.line['Description']
            obj.mediaUrls = [self.line['Lien Internet']]
            obj.durationMinutes = floor(parse_timedelta(self.line['Durée']).total_seconds()/60)
            self.eos = {}
        elif isinstance(obj, EventOccurence):
            obj.beginningDatetime = dateparser.parse(obj.idAtProviders.split('_')[1])
            obj.venue = app.model.Venue.query\
                                       .filter_by(idAtProviders=str(self.line['Ref Lieu']))\
                                       .one_or_none()
            obj.event = self.providables[0]
            self.eos[obj.idAtProviders] = obj
        elif isinstance(obj, Offer):
            obj.eventOccurence = self.eos[obj.idAtProviders]
            obj.price = 0
            obj.offerer = app.model.Offerer.query\
                                           .filter_by(idAtProviders=str(self.line['Ref Lieu']))\
                                           .one_or_none()
            if str(self.line['Places Par Horaire']).replace(' ', '') != '':
                obj.available = int(self.line['Places Par Horaire'])
        elif isinstance(obj, Mediation):
            obj.event = self.providables[0]
            obj.offerer = app.model.Offerer.query\
                                           .filter_by(idAtProviders=str(self.line['Ref Lieu']))\
                                           .one_or_none()
            if str(self.line['Texte Accroche']).replace(' ', '') != '':
                obj.text = str(self.line['Texte Accroche'])

        else:
            raise ValueError('Unexpected object class in updateObj '
                             + obj.__class__.__name__)

    def getDeactivatedObjectIds(self):
        # TODO !
        return []

    def getObjectThumb(self, obj, index):
        assert obj.idAtProviders == str(self.line['Ref Évènement'])
        thumb_request = None
        if isinstance(obj, Mediation) and 'Lien Image Accroche' in self.line:
            thumb_request = requests.get(self.line['Lien Image Accroche'])
        elif isinstance(obj, Event) and 'Lien Image' in self.line:
            thumb_request = requests.get(self.line['Lien Image'])
        #else:
        #    raise ValueError('Unexpected object class in updateObj '
        #                     + obj.__class__.__name__)
        print('thumb_request', thumb_request)
        if thumb_request and thumb_request.status_code == 200:
            return thumb_request.content

    def getObjectThumbDates(self, obj):
        if self.mock:
            return []
        if (isinstance(obj, Event) and str(self.line.get('Lien Image')).replace(' ', '') != '') or\
           (isinstance(obj, Mediation) and str(self.line.get('Lien Image Accroche')).replace(' ', '') != ''):
            return [read_date(str(self.line['Date MAJ']))]
            return read_date(str(self.line['Date MAJ']))
        else:
            return []


app.local_providers.SpreadsheetExpOffers = SpreadsheetExpOffers
