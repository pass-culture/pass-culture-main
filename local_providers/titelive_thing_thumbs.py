import re
from datetime import datetime
from io import BytesIO
from pathlib import PurePath

from connectors.ftp_titelive import get_files_to_process_from_titelive_ftp, get_zip_file_from_ftp
from domain.titelive import get_date_from_filename
from models.local_provider import LocalProvider, ProvidableInfo
from models.local_provider_event import LocalProviderEventType
from models import Product

from repository import local_provider_event_queries
from utils.logger import logger

DATE_REGEXP = re.compile('livres_tl(\d+).zip')
THUMB_FOLDER_NAME_TITELIVE = 'Atoo'


class TiteLiveThingThumbs(LocalProvider):
    help = ""
    identifierDescription = "Pas d'identifiant nécessaire" \
                            + "(on synchronise tout)"
    identifierRegexp = None
    name = "TiteLive (Epagine / Place des libraires.com) Thumbs"
    objectType = Product
    canCreate = False

    def __init__(self):
        super().__init__()

        all_zips = get_files_to_process_from_titelive_ftp(THUMB_FOLDER_NAME_TITELIVE, DATE_REGEXP)

        self.zips = self.get_remaining_files_to_check(all_zips)
        self.thumb_zipinfos = None
        self.zip = None

    def open_next_file(self):
        if self.zip:
            self.logEvent(LocalProviderEventType.SyncPartEnd,
                          get_date_from_filename(self.zip, DATE_REGEXP))
        next_zip_file_name = str(next(self.zips))
        self.zip = get_zip_file_from_ftp(next_zip_file_name, THUMB_FOLDER_NAME_TITELIVE)

        logger.info("  Importing thumbs from file " + str(self.zip))
        self.logEvent(LocalProviderEventType.SyncPartStart,
                      get_date_from_filename(self.zip, DATE_REGEXP))

        self.thumb_zipinfos = iter(filter(lambda f: f.filename.lower().endswith('_75.jpg'),
                                          sorted(self.zip.infolist(),
                                                 key=lambda f: f.filename)))

    def __next__(self):
        if self.thumb_zipinfos is None:
            self.open_next_file()

        try:
            self.thumb_zipinfo = next(self.thumb_zipinfos)
        except StopIteration:
            self.open_next_file()
            self.thumb_zipinfo = next(self.thumb_zipinfos)

        providable_info = ProvidableInfo()
        providable_info.type = Product
        providable_info.dateModifiedAtProvider = None
        path = PurePath(self.thumb_zipinfo.filename)
        providable_info.idAtProviders = path.name.split('_', 1)[0]
        self.thingId = providable_info.idAtProviders

        return providable_info

    def getObjectThumbDates(self, thing: Product) -> list:
        assert thing.idAtProviders == self.thingId
        zip_datetime = self.thumb_zipinfo.date_time
        thumb_index = extract_thumb_index(self.thumb_zipinfo.filename)
        return get_thumb_date_at_thumb_index(thumb_index, datetime(*zip_datetime))

    def getObjectThumb(self, thing: Product, index: int) -> BytesIO:
        assert thing.idAtProviders == self.thingId
        expected_index = extract_thumb_index(self.thumb_zipinfo.filename)
        assert index == expected_index
        with self.zip.open(self.thumb_zipinfo) as f:
            return f.read()

    def get_remaining_files_to_check(self, all_zips):
        latest_sync_part_end_event = local_provider_event_queries.find_latest_sync_part_end_event(self.dbObject)

        if latest_sync_part_end_event is None:
            return iter(all_zips)
        else:
            payload = int(latest_sync_part_end_event.payload)
            return iter(filter(lambda z: get_date_from_filename(z, DATE_REGEXP) > payload,
                               all_zips))


def extract_thumb_index(filename: str) -> int:
    return int(filename.split('_')[-2]) - 1


def get_thumb_date_at_thumb_index(thumb_index: int, thumb_date: datetime) -> list:
    return [None] * thumb_index + [thumb_date]
