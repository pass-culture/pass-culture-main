from datetime import datetime
import email.utils as eut
from flask import current_app as app
from psycopg2.extras import DateTimeRange
import requests

from utils.string_processing import read_date


def make_url(page, id):
    return 'https://openagenda.com/agendas/'\
           + str(id)\
           + '/events.json?'\
           + 'page='+str(page)\
           + '&limit=100'


def read_date(date):
    return datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ")


Event = app.model.Event
EventType = app.model.EventType


class OpenAgendaEvents(app.model.LocalProvider):

    help = "Si l'agenda utilisé ne contient pas que vos propres "\
           + "evenements, il est possible d'ajouter dans l'adresse "\
           + "de l'agenda des parametres de filtrage. "\
           + "Voir https://openagenda.zendesk.com/hc/fr/articles/210127965-Les-diff%C3%A9rentes-URLs-de-votre-agenda-int%C3%A9gr%C3%A9"
    identifierDescription = "Identifiant de l'agenda (ex: 80942872)"
    identifierRegexp = "^\d+$"
    name = "Open Agenda"
    objectType = Event

    def __init__(self, venue):
        super().__init__(venue)
        self.seen_uids = []
        self.page = 0
        self.index = -1
        self.more_pages = True
        self.data = None

    def __next__(self):
        self.index = self.index + 1

        if (self.data is None or len(self.data['events']) <= self.index):

            if (not self.more_pages):
                raise(StopIteration)

            self.page = self.page+1
            self.index = 0

            page_url = make_url(self.page, self.venue.idAtOfferProvider)
            req_result = requests.get(page_url)
            self.data = req_result.json()

            total_objects = self.data['offset']+self.data['limit']
            self.more_pages = total_objects < self.data['total']

        self.oa_event = self.data['events'][self.index]

        self.seen_uids.append(str(self.oa_event['uid']))

        p_info = app.model.ProvidableInfo()
        p_info.type = Event
        p_info.idAtProviders = str(self.oa_event['uid'])
        p_info.dateModifiedAtProvider = read_date(self.oa_event['updatedAt'])

        return p_info

    def getDeactivatedObjectIds(self):
        return app.db.session.query(Event.idAtProvider)\
                             .filter(Event.provider == 'OpenAgenda',
                                     Event.venue == self.venue,
                                     ~Event.idAtProvider.in_(self.seen_uids))

    def updateObject(self, event):
        assert event.idAtProviders == str(self.oa_event['uid'])
        event.description = self.oa_event['description']['fr']
        event.longDescription = self.oa_event['longDescription']\
                                and self.oa_event['longDescription']['fr']
        event.name = self.oa_event['title']['fr']
        event.extraData['tags'] = list(map(lambda t: t['slug'], self.oa_event['tags']))

        event.times = []
        for oa_timing in self.oa_event['timings']:
            event.times.append(DateTimeRange(read_date(oa_timing['start']),
                                             read_date(oa_timing['end'])))

        # TODO
        # for access in oa_event['accessibility']:
        #     event.accessibility = event.accessibility

    def getObjectThumbDates(self, event):
        assert event.idAtProvider == str(self.oa_event['uid'])
        if 'thumbnail' in self.oa_event and self.oa_event['thumbnail']:
            thumb_request = requests.head(self.oa_event['thumbnail'])
            if thumb_request.status_code == 200:
                date = thumb_request.headers['Last-Modified']\
                       or thumb_request.headers['Date']
                if date is None:
                    return None
                else:
                    return [datetime(*eut.parsedate(date)[:6])]
        else:
            return []

    def getObjectThumb(self, event, index):
        assert event.idAtProvider == str(self.oa_event['uid'])
        thumb_request = requests.get(self.oa_event['thumbnail'])
        if thumb_request.status_code == 200:
            return thumb_request.content


app.local_providers.OpenAgendaEvents = OpenAgendaEvents
