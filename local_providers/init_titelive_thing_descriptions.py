import re
from pathlib import PurePath, Path

import os
from zipfile import ZipFile

from datetime import datetime

from domain.titelive import get_date_from_filename, read_description_date
from models.local_provider import LocalProvider, ProvidableInfo
from models.local_provider_event import LocalProviderEventType
from models.thing import Thing
from utils.logger import logger

DATE_REGEXP = re.compile('Resume-full_(\d{8}).zip')
INIT_TITELIVE_DESCRIPTION_DATE_FORMAT = "%d%m%Y"
END_FILE_IDENTIFIER = '_p.txt'


class InitTiteLiveThingDescriptions(LocalProvider):
    help = ""
    identifierDescription = "Pas d'identifiant nécessaire" \
                            + "(on synchronise tout)"
    identifierRegexp = None
    name = "Init TiteLive Descriptions"
    objectType = Thing
    canCreate = False

    def __init__(self, titelive_file: str, **options):
        super().__init__(**options)

        file_path = Path(os.path.dirname(os.path.realpath(__file__))) \
                    / '..' / titelive_file
        self.zip = ZipFile(file_path)
        self.desc_zipinfos = None
        self.date_modified = None

    def open_next_file(self):
        if self.zip:
            self.logEvent(LocalProviderEventType.SyncPartEnd,
                          get_date_from_filename(self.zip, DATE_REGEXP))

        logger.info("  Importing descriptions from file " + str(self.zip))
        self.logEvent(LocalProviderEventType.SyncPartStart,
                      get_date_from_filename(self.zip, DATE_REGEXP))

        self.desc_zipinfos = self.get_description_files_from_zip_info()
        tmp_date = str(get_date_from_filename(self.zip, DATE_REGEXP))
        logger.info(tmp_date)
        self.date_modified = self.read_description_date(tmp_date)

    def __next__(self):
        if self.desc_zipinfos is None:
            self.open_next_file()

        try:
            self.desc_zipinfo = next(self.desc_zipinfos)
        except StopIteration:
            self.open_next_file()
            self.desc_zipinfo = next(self.desc_zipinfos)

        providable_info = ProvidableInfo()
        providable_info.type = Thing
        providable_info.dateModifiedAtProvider = self.date_modified
        path = PurePath(self.desc_zipinfo.filename)
        providable_info.idAtProviders = path.name.split('_', 1)[0]
        self.thingId = providable_info.idAtProviders

        return providable_info

    def updateObject(self, thing):
        with self.zip.open(self.desc_zipinfo) as f:
            thing.description = f.read().decode('iso-8859-1')

    def get_description_files_from_zip_info(self):
        sorted_files = sorted(self.zip.infolist(), key=lambda f: f.filename)
        filtered_files = filter(lambda f: f.filename.lower().endswith(END_FILE_IDENTIFIER), sorted_files)
        return iter(filtered_files)

    def read_description_date(self, date):
        return datetime.strptime(date, INIT_TITELIVE_DESCRIPTION_DATE_FORMAT)
