import re
from datetime import datetime
from os import path
from zipfile import ZipFile

from flask import current_app as app
from pandas import read_excel

from models.event import Event
from models.local_provider import LocalProvider
from models.offer import Offer
from utils.human_ids import humanize
from utils.object_storage import local_path
from utils.string_processing import get_date_time_range, get_matched_string_index, get_price_value, read_date

DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
image_extension_regex = re.compile(r'jpg|JPG|png|PNG')
thumb_target_keys = ['Titre', 'Artiste']

Event = Event
Offer = Offer


class SpreadsheetOffers(LocalProvider):
    help = "Pas d'aide pour le moment"
    identifierDescription = "Nom de la librairie"
    identifierRegexp = "^\w+$"
    name = "Spreadsheet Offers"
    objectType = Offer
    canCreate = True

    def __init__(self, offerer):
        super().__init__(offerer)
        #init
        self.human_id = humanize(offerer.id)
        self.index = 0
        # spreadsheet from the offerer
        self.spreadsheet_dir = local_path('spreadsheets', 'offerers/' + self.human_id)
        if not path.isfile(self.spreadsheet_dir):
            print('did not find ' + str(self.spreadsheet_dir))
            return
        self.df = read_excel(self.spreadsheet_dir)
        # self.iterations_count = self.df.shape[0]
        self.iterations_count = 2
        # clean (because actually several rows match for one artist/titre but several dates and schedules)
        for index in range(0, self.iterations_count):
            if not isinstance(self.df['Artiste'][index], str):
                self.df['Artiste'][index] = self.df['Artiste'][index-1]
                self.df['Tarif'][index] = self.df['Tarif'][index-1]
                self.df['Titre'][index] = self.df['Titre'][index-1]
                if not isinstance(self.df['Dates'][index], str):
                    self.df['Dates'][index] = self.df['Dates'][index-1]
                if not isinstance(self.df['Horaires'][index], str):
                    self.df['Horaires'][index] = self.df['Horaires'][index-1]
                self.df['Durée'][index] = self.df['Durée'][index-1]
        # zip of thumbs given by the offerer
        # in which the name of the file should be sufficiently close
        # to a column titre of one of the row of self.df to be attached with
        self.zip_dir = local_path('zips', 'offerers/' + self.human_id)
        if not path.isfile(self.zip_dir):
            print('did not find ' + str(self.zip_dir))
            return
        self.zip = ZipFile(str(self.zip_dir))
        self.zip_names = self.zip.namelist()
        # create something easy to grab and match (<image_dir>, <re image>)
        self.thumb_dirs = list(filter(
            lambda zip_name: re.match(
                image_extension_regex,
                zip_name.split('.')[-1]
            ) and len(zip_name.split('/')) == 2,
            self.zip_names
        ))
        self.thumb_names = list(map(
            lambda thumb_dir: thumb_dir.split('/')[1].split('.')[0],
            self.thumb_dirs
        ))
        self.df = self.df.assign(Image=list(map(
            lambda strings: " ".join(map(
                lambda string: string if isinstance(string, str) else "",
                strings
            )),
            zip(*map(lambda key: list(self.df[key].values), thumb_target_keys))
        )))
        # date
        self.dateNow = datetime.utcnow()
        self.dateModified = self.dateNow.strftime(DATE_FORMAT)

    def __next__(self):
        if (self.index > self.iterations_count - 1):
            raise(StopIteration)

        values = self.df.values[self.index, :]
        self.sp_event = dict(zip(self.df.columns, values))

        self.index = self.index + 1

        p_info_event = ProvidableInfo()
        p_info_event.type = Event
        p_info_event.idAtProviders = str(self.dateModified + '-' + str(self.index))
        p_info_event.dateModifiedAtProvider = read_date(self.dateModified)

        p_info_offer = ProvidableInfo()
        p_info_offer.type = Offer
        p_info_offer.idAtProviders = str(self.dateModified + '-' + str(self.index))
        p_info_offer.dateModifiedAtProvider = read_date(self.dateModified)

        return p_info_event, p_info_offer

    def updateObject(self, offerOrEvent, providableObjs):
        if isinstance(offerOrEvent, Event):
            event = offerOrEvent
            event.description = self.sp_event.get('description')
            event.lastProvider = self.dbObject
            event.idAtProviders = str(self.dateModified + '-' + str(self.index))
            event.longDescription = self.sp_event.get('longDescription')
            event.name = self.sp_event['Titre']
            event.extraData['tags'] = list(map(lambda t: t['slug'], self.sp_event.get('tags') or []))
            event.times = get_date_time_range(
                self.sp_event['Dates'] + ' ' + self.dateNow.strftime('%Y'),
                self.sp_event.get('Horaires'),
                self.sp_event.get('Durée')
            )
        else:
            offer = offerOrEvent

            offer.price = get_price_value(self.sp_event.get('Tarif'))
            offer.event = providableObjs[0]
            offer.idAtProviders = event.idAtProvider
            offer.name = event.name

    def getDeactivatedObjectIds(self):
        return []

    def getDeletedObjectUids(self):
        return []

    def getObjectThumb(self, obj, index):
        matched_thumb_index = get_matched_string_index(self.sp_event['Image'], self.thumb_names)
        return self.zip.read(self.thumb_dirs[matched_thumb_index])

    def getObjectThumbDates(self, obj):
        return [self.dateNow]


app.local_providers.SpreadsheetOffers = SpreadsheetOffers
