import re
from datetime import datetime
from io import BytesIO
from pathlib import PurePath
from typing import List

from connectors.ftp_titelive import get_files_to_process_from_titelive_ftp, get_zip_file_from_ftp
from domain.titelive import get_date_from_filename
from local_providers.local_provider import LocalProvider
from local_providers.providable_info import ProvidableInfo
from models.local_provider_event import LocalProviderEventType
from models import Product

from repository import local_provider_event_queries
from utils.logger import logger

DATE_REGEXP = re.compile('livres_tl(\d+).zip')
THUMB_FOLDER_NAME_TITELIVE = 'Atoo'
SYNCHONISABLE_FILE_EXTENSION = '_75.jpg'


class TiteLiveThingThumbs(LocalProvider):
    help = ""
    identifier_description = "Pas d'identifiant nécessaire" \
                            + "(on synchronise tout)"
    identifier_regexp = None
    name = "TiteLive (Epagine / Place des libraires.com) Thumbs"
    object_type = Product
    can_create = False

    def __init__(self):
        super().__init__()

        all_zips = get_files_to_process_from_titelive_ftp(THUMB_FOLDER_NAME_TITELIVE, DATE_REGEXP)

        self.zips = self.get_remaining_files_to_check(all_zips)
        self.thumb_zipinfos = None
        self.zip = None

    def open_next_file(self):
        if self.zip:
            self.log_provider_event(LocalProviderEventType.SyncPartEnd,
                                    get_date_from_filename(self.zip, DATE_REGEXP))
        next_zip_file_name = str(next(self.zips))
        self.zip = get_zip_file_from_ftp(next_zip_file_name, THUMB_FOLDER_NAME_TITELIVE)

        logger.info("  Importing thumbs from file " + str(self.zip))
        self.log_provider_event(LocalProviderEventType.SyncPartStart,
                                get_date_from_filename(self.zip, DATE_REGEXP))

        self.thumb_zipinfos = iter(filter(lambda f: f.filename.lower().endswith(SYNCHONISABLE_FILE_EXTENSION),
                                          sorted(self.zip.infolist(),
                                                 key=lambda f: f.filename)))

    def __next__(self) -> List[ProvidableInfo]:
        if self.thumb_zipinfos is None:
            self.open_next_file()

        try:
            self.thumb_zipinfo = next(self.thumb_zipinfos)
        except StopIteration:
            self.open_next_file()
            self.thumb_zipinfo = next(self.thumb_zipinfos)

        path = PurePath(self.thumb_zipinfo.filename)

        providable_info = ProvidableInfo()
        providable_info.type = Product
        providable_info.date_modified_at_provider = datetime(*self.thumb_zipinfo.date_time)
        providable_info.id_at_providers = path.name.split('_', 1)[0]
        self.thingId = providable_info.id_at_providers

        return [providable_info]

    def get_object_thumb_index(self) -> int:
        return extract_thumb_index(self.thumb_zipinfo.filename)

    def get_object_thumb_date(self, thing: Product) -> datetime:
        thumbs_batch_datetime = self.thumb_zipinfo.date_time
        return datetime(*thumbs_batch_datetime)

    def getObjectThumb(self, thing: Product, index: int) -> BytesIO:
        assert thing.idAtProviders == self.thingId
        expected_index = extract_thumb_index(self.thumb_zipinfo.filename)
        assert index == expected_index
        with self.zip.open(self.thumb_zipinfo) as f:
            return f.read()

    def get_remaining_files_to_check(self, all_zips):
        latest_sync_part_end_event = local_provider_event_queries.find_latest_sync_part_end_event(self.provider)

        if latest_sync_part_end_event is None:
            return iter(all_zips)
        else:
            payload = int(latest_sync_part_end_event.payload)
            return iter(filter(lambda z: get_date_from_filename(z, DATE_REGEXP) > payload,
                               all_zips))

    def fill_object_attributes(self, obj):
        pass


def extract_thumb_index(filename: str) -> int:
    split_filename = filename.split('_')
    if len(split_filename) > 2:
        return int(split_filename[-2]) - 1
    return None
