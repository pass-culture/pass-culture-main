import re
from pathlib import PurePath, Path

import os
from zipfile import ZipFile

from datetime import datetime

from domain.titelive import get_date_from_filename
from models.local_provider import LocalProvider, ProvidableInfo
from models.thing import Thing
from utils.logger import logger

DATE_REGEXP = re.compile('Resume-full_(\d{8}).zip')
INIT_TITELIVE_DESCRIPTION_DATE_FORMAT = "%d%m%Y"
END_FILE_NAME_IDENTIFIER = '_p.txt'


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
        self.description_zip_infos = None
        self.date_modified = None

    def open_next_file(self):
        logger.info("Importing descriptions from file " + str(self.zip))
        self.description_zip_infos = self.get_description_files_from_zip_info()
        file_date = str(get_date_from_filename(self.zip, DATE_REGEXP))
        self.date_modified = self.read_description_date(file_date)

    def __next__(self):
        if self.description_zip_infos is None:
            self.open_next_file()

        self.description_zipinfo = next(self.description_zip_infos)

        providable_info = ProvidableInfo()
        providable_info.type = Thing
        providable_info.dateModifiedAtProvider = self.date_modified
        path = PurePath(self.description_zipinfo.filename)
        providable_info.idAtProviders = path.name.split('_', 1)[0]
        self.thingId = providable_info.idAtProviders

        return providable_info

    def updateObject(self, thing):
        with self.zip.open(self.description_zipinfo) as f:
            thing.description = f.read().decode('iso-8859-1')

    def get_description_files_from_zip_info(self):
        sorted_files = sorted(self.zip.infolist(), key=lambda f: f.filename)
        filtered_files = filter(lambda f: f.filename.lower().endswith(END_FILE_NAME_IDENTIFIER), sorted_files)
        return iter(filtered_files)

    def read_description_date(self, date):
        return datetime.strptime(date, INIT_TITELIVE_DESCRIPTION_DATE_FORMAT)
