import re
from pathlib import PurePath

from models.local_provider import LocalProvider, ProvidableInfo
from models.local_provider_event import LocalProviderEventType
from models.thing import Thing
from repository import local_provider_event_queries
from utils.ftp_titelive import get_ordered_files_from_titelive_ftp, \
    get_date_from_filename, read_description_date, get_zip_file_from_ftp
from utils.logger import logger

DATE_REGEXP = re.compile('Resume(\d{6}).zip')
DESCRIPTION_FOLDER_NAME_TITELIVE = 'ResumesLivres'


class TiteLiveThingDescriptions(LocalProvider):
    help = ""
    identifierDescription = "Pas d'identifiant nécessaire" \
                            + "(on synchronise tout)"
    identifierRegexp = None
    name = "TiteLive (Epagine / Place des libraires.com) Descriptions"
    objectType = Thing
    canCreate = False

    def __init__(self):
        super().__init__()

        all_zips = get_ordered_files_from_titelive_ftp()

        self.zips = self.get_remaining_files_to_check(all_zips)
        self.desc_zipinfos = None
        self.zip = None
        self.dateModified = None

    def open_next_file(self):
        if self.zip:
            self.logEvent(LocalProviderEventType.SyncPartEnd,
                          get_date_from_filename(self.zip, DATE_REGEXP))
        next_zip_file_name = str(self.zips.__next__())
        self.zip = get_zip_file_from_ftp(next_zip_file_name, DESCRIPTION_FOLDER_NAME_TITELIVE)

        logger.info("  Importing descriptions from file " + str(self.zip))
        self.logEvent(LocalProviderEventType.SyncPartStart,
                      get_date_from_filename(self.zip, DATE_REGEXP))

        self.desc_zipinfos = iter(filter(lambda f: f.filename.lower().endswith('_p.txt'),
                                         sorted(self.zip.infolist(),
                                                key=lambda f: f.filename)))
        self.desc_zipinfos = iter(filter(lambda f: f.filename.lower()
                                         .endswith('_p.txt'),
                                         self.zip.infolist()))
        self.dateModified = read_description_date(str(get_date_from_filename(self.zip, DATE_REGEXP)))

    def __next__(self):
        if self.desc_zipinfos is None:
            self.open_next_file()

        try:
            self.desc_zipinfo = self.desc_zipinfos.__next__()
        except StopIteration:
            self.open_next_file()
            self.desc_zipinfo = self.desc_zipinfos.__next__()

        providable_info = ProvidableInfo()
        providable_info.type = Thing
        providable_info.dateModifiedAtProvider = self.dateModified
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
