import re
from pathlib import PurePath

from connectors.ftp_titelive import get_files_to_process_from_titelive_ftp, get_zip_file_from_ftp
from domain.titelive import get_date_from_filename, read_description_date
from models.local_provider import LocalProvider, ProvidableInfo
from models import Product
from models.local_provider_event import LocalProviderEventType

from repository import local_provider_event_queries
from utils.logger import logger

DATE_REGEXP = re.compile('Resume(\d{6}).zip')
DESCRIPTION_FOLDER_NAME_TITELIVE = 'ResumesLivres'
END_FILE_IDENTIFIER = '_p.txt'


class TiteLiveThingDescriptions(LocalProvider):
    help = ""
    identifierDescription = "Pas d'identifiant nécessaire" \
                            + "(on synchronise tout)"
    identifierRegexp = None
    name = "TiteLive (Epagine / Place des libraires.com) Descriptions"
    objectType = Product
    canCreate = False

    def __init__(self):
        super().__init__()

        all_zips = get_files_to_process_from_titelive_ftp()

        self.zips = self.get_remaining_files_to_check(all_zips)
        self.desc_zipinfos = None
        self.zip = None
        self.date_modified = None

    def open_next_file(self):
        if self.zip:
            self.logEvent(LocalProviderEventType.SyncPartEnd,
                          get_date_from_filename(self.zip, DATE_REGEXP))
        next_zip_file_name = str(next(self.zips))
        self.zip = get_zip_file_from_ftp(next_zip_file_name, DESCRIPTION_FOLDER_NAME_TITELIVE)

        logger.info("  Importing descriptions from file " + str(self.zip))
        self.logEvent(LocalProviderEventType.SyncPartStart,
                      get_date_from_filename(self.zip, DATE_REGEXP))

        self.desc_zipinfos = self.get_description_files_from_zip_info()

        self.date_modified = read_description_date(str(get_date_from_filename(self.zip, DATE_REGEXP)))

    def __next__(self):
        if self.desc_zipinfos is None:
            self.open_next_file()

        try:
            self.desc_zipinfo = next(self.desc_zipinfos)
        except StopIteration:
            self.open_next_file()
            self.desc_zipinfo = next(self.desc_zipinfos)

        providable_info = ProvidableInfo()
        providable_info.type = Product
        providable_info.dateModifiedAtProvider = self.date_modified
        path = PurePath(self.desc_zipinfo.filename)
        providable_info.idAtProviders = path.name.split('_', 1)[0]
        self.thingId = providable_info.idAtProviders

        return providable_info

    def updateObject(self, thing):
        with self.zip.open(self.desc_zipinfo) as f:
            thing.description = f.read().decode('iso-8859-1')

    def get_remaining_files_to_check(self, all_zips):
        latest_sync_part_end_event = local_provider_event_queries.find_latest_sync_part_end_event(self.dbObject)

        if latest_sync_part_end_event is None:
            return iter(all_zips)
        else:
            return iter(
                filter(lambda z: get_date_from_filename(z, DATE_REGEXP) > int(latest_sync_part_end_event.payload),
                       all_zips))

    def get_description_files_from_zip_info(self):
        sorted_files = sorted(self.zip.infolist(), key=lambda f: f.filename)
        filtered_files = filter(lambda f: f.filename.lower().endswith(END_FILE_IDENTIFIER), sorted_files)
        return iter(filtered_files)
