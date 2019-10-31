import re
from pathlib import PurePath
from typing import List

from connectors.ftp_titelive import get_files_to_process_from_titelive_ftp, get_zip_file_from_ftp
from domain.titelive import get_date_from_filename, read_description_date
from local_providers.local_provider import LocalProvider
from local_providers.providable_info import ProvidableInfo
from models import Product
from models.local_provider_event import LocalProviderEventType
from repository import local_provider_event_queries
from utils.logger import logger

DATE_REGEXP = re.compile('Resume(\d{6}).zip')
DESCRIPTION_FOLDER_NAME_TITELIVE = 'ResumesLivres'
END_FILE_IDENTIFIER = '_p.txt'


class TiteLiveThingDescriptions(LocalProvider):
    name = "TiteLive (Epagine / Place des libraires.com) Descriptions"
    can_create = False

    def __init__(self):
        super().__init__()

        all_zips = get_files_to_process_from_titelive_ftp(DESCRIPTION_FOLDER_NAME_TITELIVE, DATE_REGEXP)

        self.zips = self.get_remaining_files_to_check(all_zips)
        self.description_zipinfos = None
        self.zip_file = None
        self.date_modified = None

    def __next__(self) -> List[ProvidableInfo]:
        if self.description_zipinfos is None:
            self.open_next_file()

        try:
            self.description_zipinfo = next(self.description_zipinfos)
        except StopIteration:
            self.open_next_file()
            self.description_zipinfo = next(self.description_zipinfos)

        path = PurePath(self.description_zipinfo.filename)
        product_providable_info = self.create_providable_info(Product,
                                                              path.name.split('_', 1)[0],
                                                              self.date_modified)
        self.thingId = product_providable_info.id_at_providers
        return [product_providable_info]

    def fill_object_attributes(self, product: Product):
        with self.zip_file.open(self.description_zipinfo) as f:
            product.description = f.read().decode('iso-8859-1')

    def open_next_file(self):
        if self.zip_file:
            self.log_provider_event(LocalProviderEventType.SyncPartEnd,
                                    get_date_from_filename(self.zip_file, DATE_REGEXP))
        next_zip_file_name = str(next(self.zips))
        self.zip_file = get_zip_file_from_ftp(next_zip_file_name, DESCRIPTION_FOLDER_NAME_TITELIVE)

        logger.info("  Importing descriptions from file " + str(self.zip_file))
        self.log_provider_event(LocalProviderEventType.SyncPartStart,
                                get_date_from_filename(self.zip_file, DATE_REGEXP))

        self.description_zipinfos = self.get_description_files_from_zip_info()

        self.date_modified = read_description_date(str(get_date_from_filename(self.zip_file, DATE_REGEXP)))

    def get_remaining_files_to_check(self, all_zips) -> iter:
        latest_sync_part_end_event = local_provider_event_queries.find_latest_sync_part_end_event(self.provider)

        if latest_sync_part_end_event is None:
            return iter(all_zips)
        else:
            return iter(
                filter(lambda z: get_date_from_filename(z, DATE_REGEXP) > int(latest_sync_part_end_event.payload),
                       all_zips))

    def get_description_files_from_zip_info(self) -> iter:
        sorted_files = sorted(self.zip_file.infolist(), key=lambda f: f.filename)
        filtered_files = filter(lambda f: f.filename.lower().endswith(END_FILE_IDENTIFIER), sorted_files)
        return iter(filtered_files)
