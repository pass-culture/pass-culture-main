from datetime import datetime
import email.utils as eut
from flask import current_app as app
import json
import math
import os
from pathlib import Path
from psycopg2.extras import DateTimeRange
import requests


def make_url(page, id):
    return 'https://openagenda.com/agendas/'\
           + str(id)\
           + '/events.json?'\
           + 'page='+str(page)\
           + '&limit=100'


def get_data(page, id, is_mock):
    if is_mock:
        with open(Path(os.path.dirname(os.path.realpath(__file__)))
                    / '..' / 'mock' / 'providers'
                    / ('openagenda' + str(page) + '.json')) as f:
            return json.load(f)
    else:
        page_url = make_url(page, id)
        req_result = requests.get(page_url)
        return req_result.json()


def read_date(date):
    return datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ")


Event = app.model.Event
EventOccurence = app.model.EventOccurence


class OpenAgendaEvents(app.model.LocalProvider):
    help = ""
    identifierDescription = "Identifiant de l'agenda (ex: 80942872). Il se trouve à la fin de l'adresse web de votre agenda."
    identifierRegexp = "^\d+$"
    name = "Open Agenda"
    objectType = Event
    canCreate = True

    def __init__(self, venueProvider, **options):
        super().__init__(venueProvider, **options)
        self.venue = app.model.Venue.query\
                                    .filter_by(id=self.venueProvider.venueId)\
                                    .one_or_none()
        self.is_mock = 'mock' in options and options['mock']
        self.seen_uids = []
        self.page = 0
        self.index = -1
        self.more_pages = True
        self.data = None
        self.venueLocationUid = None

    def __next__(self):
        self.index = self.index + 1

        if (self.data is None or len(self.data['events']) <= self.index):

            if (not self.more_pages):
                raise(StopIteration)

            self.page = self.page+1
            self.index = 0

            self.data = get_data(self.page,
                                 self.venueProvider.venueIdAtOfferProvider,
                                 self.is_mock)

            total_objects = self.data['offset']+self.data['limit']
            self.more_pages = total_objects < self.data['total']

        self.oa_event = self.data['events'][self.index]

        self.seen_uids.append(str(self.oa_event['uid']))

        if self.venueLocationUid is not None and\
           self.oa_event['location']['uid'] != self.venueLocationUid:
            return self.__next__()
        
        p_info_event = app.model.ProvidableInfo()
        p_info_event.type = Event
        p_info_event.idAtProviders = str(self.oa_event['uid'])
        p_info_event.dateModifiedAtProvider = read_date(self.oa_event['updatedAt'])

        p_info_eos = []
        durations_sum = 0
        for oa_timing in self.oa_event['timings']:
            p_info_eo = app.model.ProvidableInfo()
            p_info_eo.type = EventOccurence
            p_info_eo.idAtProviders = str(self.oa_event['uid'])+'_'+str(read_date(oa_timing['start']))
            p_info_eo.dateModifiedAtProvider = read_date(self.oa_event['updatedAt'])
            p_info_eos.append(p_info_eo)
            duration = read_date(oa_timing['end'])\
                        - read_date(oa_timing['start'])
            durations_sum += duration.days*24*60 + int(duration.seconds/60)

        self.duration = int(durations_sum / len(p_info_eos))

        return [p_info_event] + p_info_eos

    def getDeactivatedObjectIds(self):
        return app.db.session.query(Event.idAtProviders)\
                             .filter(Event.provider == 'OpenAgenda',
                                     Event.venue == self.venue,
                                     ~Event.idAtProviders.in_(self.seen_uids))

    def updateObject(self, obj):
        if isinstance(obj, Event):
            assert obj.idAtProviders == str(self.oa_event['uid'])
            obj.name = self.oa_event['title']['fr']\
                       or self.oa_event['title']['en']
            obj.description = self.oa_event['description']['fr']\
                              or self.oa_event['description']['en']
            obj.durationMinutes = self.duration
            # obj.extraData['tags'] = list(map(lambda t: t['slug'], self.oa_event['tags']))
        elif isinstance(obj, EventOccurence):
            index = len(self.providables)-2
            oa_timing = self.oa_event['timings'][index]
            obj.beginningDatetime = read_date(oa_timing['start'])
            obj.endDatetime = read_date(oa_timing['end'])
            obj.event = self.providables[0]
        else:
            raise ValueError('Unexpected object class in updateObject: '
                             + obj.__class__.__name__)


        # TODO
        # for access in oa_event['accessibility']:
        #     event.accessibility = event.accessibility

    def getObjectThumbDates(self, obj):
        if not isinstance(obj, Event):
            return []
        assert obj.idAtProviders == str(self.oa_event['uid'])
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
        assert event.idAtProviders == str(self.oa_event['uid'])
        thumb_request = requests.get(self.oa_event['thumbnail'])
        if thumb_request.status_code == 200:
            return thumb_request.content

    def updateObjects(self, limit=None):
        #self.computeVenueLocationUid()
        super().updateObjects(limit)

    def computeVenueLocationUid(self):
        more_pages = True
        page = 0
        locations = {}
        venue = self.venue
        while more_pages:
            page += 1
            data = get_data(page,
                            self.venueProvider.venueIdAtOfferProvider,
                            self.is_mock)
            for event in data:
                loc = event['location']
                locations[loc['uid']] = loc
            total_objects = data['offset'] + data['limit']
            more_pages = total_objects < data['total']
        if len(locations) == 0:
            return
        locations_by_distance = sorted(locations.values,
                                       lambda l: math.sqrt((l.latitude - venue.latitude) ** 2
                                                           + (l.longitude - venue.longitude) ** 2))
        self.venueLocationUid = locations_by_distance[0]['uid']


app.local_providers.OpenAgendaEvents = OpenAgendaEvents
