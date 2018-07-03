""" spreadsheet exp offers"""
from datetime import datetime, timedelta
import dateparser
from flask import current_app as app
from os import path
from pandas import read_csv
from pathlib import Path
import re

from utils.date import format_duration


DATE_FORMAT = "%d/%m/%Y %Hh%M"
HOUR_REGEX = re.compile(r"(\d)h(\d?)$", re.IGNORECASE)


def read_date(date):
    return datetime.strptime(date, DATE_FORMAT)


def is_filled(info):
    info = str(info)
    return info != 'nan' and info.replace(' ', '') != ''


Event = app.model.Event
EventOccurence = app.model.EventOccurence
Mediation = app.model.Mediation
Occasion = app.model.Occasion
Offer = app.model.Offer


class SpreadsheetExpOffers(app.model.LocalProvider):
    help = "Pas d'aide pour le moment"
    identifierDescription = "Pas d'identifiant nécessaire"\
                            + "(on synchronise tout)"
    identifierRegexp = None
    name = "Experimentation Spreadsheet (Offres)"
    objectType = Offer
    canCreate = True

    def __init__(self, offerer, mock=False):
        super().__init__(offerer)
        if mock:
            self.df = read_csv(Path(path.dirname(path.realpath(__file__))) / '..' / 'mock' / 'spreadsheet_exp' / 'Evenements.csv')
        else:
            self.df = read_csv('https://docs.google.com/spreadsheets/d/1Lj53_cgWDyQ1BqUeVtq059nXxOULL28mDmm_3p2ldpo/gviz/tq?tqx=out:csv&sheet=Evenements')
        self.lines = self.df.iterrows()
        self.mock = mock

    def __next__(self):
        self.line = self.lines.__next__()[1]

        for field in ['Date MAJ', 'Description', 'Horaires', 'Ref Lieu', 'Ref Évènement', 'Durée', 'Places Par Horaire']:
            while not is_filled(self.line[field]):
                print(field+' is empty, skipping line')
                self.__next__()

        venueIdAtProviders = str(int(self.line['Ref Lieu']))

        self.venue = app.model.Venue.query\
                                    .filter_by(idAtProviders=venueIdAtProviders)\
                                    .one_or_none()

        if self.venue is None:
            print('Venue #' + venueIdAtProviders
                  + ' not found, skipping line')
            self.__next__()

        self.offerer = app.model.Offerer.query\
                                        .filter_by(idAtProviders=venueIdAtProviders)\
                                        .one_or_none()

        if self.offerer is None:
            print('Offerer #' + venueIdAtProviders
                  + ' not found, skipping line')
            self.__next__()

        providables = []

        p_info_event = app.model.ProvidableInfo()
        p_info_event.type = Event
        p_info_event.idAtProviders = str(int(self.line['Ref Évènement']))
        p_info_event.dateModifiedAtProvider = read_date(self.line['Date MAJ'])

        providables.append(p_info_event)

        p_info_occasion = app.model.ProvidableInfo()
        p_info_occasion.type = Occasion
        p_info_occasion.idAtProviders = str(int(self.line['Ref Évènement']))
        p_info_occasion.dateModifiedAtProvider = read_date(self.line['Date MAJ'])

        providables.append(p_info_occasion)

        for index, horaire in enumerate(self.line['Horaires'].split(';')):
            if is_filled(horaire):
                horaire = HOUR_REGEX.sub(r'\1:\2', horaire.strip())
                if horaire.endswith(':'):
                    horaire = horaire + '00'
                evocc_dt = dateparser.parse(horaire, languages=['fr'])
                if evocc_dt is None:
                    print("Could not parse date : '"+horaire+"'")

                p_info_evocc = app.model.ProvidableInfo()
                p_info_evocc.type = EventOccurence
                p_info_evocc.idAtProviders = str(int(self.line['Ref Évènement'])) + '_'\
                                             + evocc_dt.isoformat()
                p_info_evocc.dateModifiedAtProvider = read_date(self.line['Date MAJ'])

                providables.append(p_info_evocc)

                p_info_offer = app.model.ProvidableInfo()
                p_info_offer.type = Offer
                p_info_offer.idAtProviders = str(int(self.line['Ref Évènement'])) + '_'\
                                             + evocc_dt.isoformat()
                p_info_offer.dateModifiedAtProvider = read_date(self.line['Date MAJ'])

                providables.append(p_info_offer)

        if is_filled(self.line['Lien Image Accroche']) or\
           is_filled(self.line['Texte Accroche']):
            p_info_med = app.model.ProvidableInfo()
            p_info_med.type = Mediation
            p_info_med.idAtProviders = str(int(self.line['Ref Évènement']))
            p_info_med.dateModifiedAtProvider = read_date(self.line['Date MAJ'])

            providables.append(p_info_med)

        return providables

    def updateObject(self, obj):
        if isinstance(obj, Event):
            obj.name = self.line['Titre']
            obj.description = self.line['Description']
            obj.mediaUrls = [self.line['Lien Internet']]
            obj.durationMinutes = format_duration(self.line['Durée'])
            obj.isNational = is_filled(self.line["Territoire\n(Reporting)"])\
                             and (str(self.line["Territoire\n(Reporting)"]) == '0'
                                  or str(self.line["Territoire\n(Reporting)"]) == '0.0')

            self.eos = {}
        elif isinstance(obj, Occasion):
            obj.venue = self.venue
            obj.event = self.providables[0]
        elif isinstance(obj, EventOccurence):
            obj.beginningDatetime = dateparser.parse(obj.idAtProviders.split('_')[1],
                                                     settings={'TIMEZONE': 'UTC-3' if self.venue.departementCode=='97'
                                                                                 else 'Europe/Paris',
                                                               'TO_TIMEZONE': 'UTC'})
            obj.endDatetime = obj.beginningDatetime\
                              + timedelta(minutes=self.providables[0].durationMinutes)
            obj.venue = self.venue
            obj.event = self.providables[0]
        elif isinstance(obj, Offer):
            for providable in self.providables[1:]:
                if isinstance(providable, EventOccurence)\
                   and providable.idAtProviders == obj.idAtProviders:
                    obj.eventOccurence = providable
                    break
            if obj.eventOccurence is None:
                raise ValueError("Can't find EventOccurence matching offer in updateObj")
            obj.price = 0
            obj.offerer = self.offerer
            if is_filled(self.line['Places Par Horaire']):
                obj.available = int(self.line['Places Par Horaire'])
        elif isinstance(obj, Mediation):
            obj.event = self.providables[0]
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
        assert obj.idAtProviders == str(int(self.line['Ref Évènement']))
        thumb_url = None
        if isinstance(obj, Mediation):
            thumb_url = self.line['Lien Image Accroche']
        elif isinstance(obj, Event):
            thumb_url = self.line['Lien Image']
        else:
            raise ValueError('Unexpected object class in updateObject: '
                             + obj.__class__.__name__)
        return thumb_url

    def getObjectThumbDates(self, obj):
        if self.mock:
            return []
        if (isinstance(obj, Event) and is_filled(self.line.get('Lien Image'))) or\
           (isinstance(obj, Mediation) and is_filled(self.line.get('Lien Image Accroche'))):
            return [read_date(str(self.line['Date MAJ']))]
        else:
            return []


app.local_providers.SpreadsheetExpOffers = SpreadsheetExpOffers
