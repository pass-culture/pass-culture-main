import re
from itertools import islice
from pathlib import Path

import os

from domain.titelive import read_things_date
from local_providers.titelive_things import get_thing_type_and_extra_data_from_titelive_type, get_infos_from_data_line, \
    get_extraData_from_infos
from models.local_provider import LocalProvider, ProvidableInfo
from models import Product
from models.local_provider_event import LocalProviderEventType, LocalProviderEvent

from utils.logger import logger
from utils.string_processing import trim_with_elipsis

DATE_REGEXP = re.compile('([a-zA-Z]+)(\d+).tit')
NUMBER_OF_ELEMENTS_PER_LINE = 46  # (45 elements from line + \n)
SYNC_PART_SIZE = 1000

class InitTiteLiveThings(LocalProvider):
    help = ""
    identifierDescription = "Pas d'identifiant nécessaire" \
                            + "(on synchronise tout)"
    identifierRegexp = None
    name = "Init TiteLive (Epagine / Place des libraires.com)"
    objectType = Product
    canCreate = True

    def __init__(self, titelive_file: str, **options):
        super().__init__(**options)

        file_path = Path(os.path.dirname(os.path.realpath(__file__))) \
                    / '..' / titelive_file
        self.thing_file = file_path

        self.data_lines = None

        last_import_commit = LocalProviderEvent.query \
            .filter_by(type=LocalProviderEventType.SyncPartEnd) \
            .filter_by(providerId=self.dbObject.id) \
            .order_by(LocalProviderEvent.date.desc()) \
            .first()
        if last_import_commit:
            self.lines_checked = int(last_import_commit.payload)
        else:
            self.lines_checked = 0
        logger.info("Starting at line : %s" % str(self.lines_checked))

    def __next__(self):
        if self.data_lines is None:
            self.data_lines = get_lines_from_thing_file(self.lines_checked, str(self.thing_file))

        try:
            data_lines = next(self.data_lines)
            elements = data_lines.split('~')
        except StopIteration:
            self.data_lines = get_lines_from_thing_file(self.lines_checked, str(self.thing_file))
            elements = next(self.data_lines).split('~')

        if len(elements) != NUMBER_OF_ELEMENTS_PER_LINE:
            logger.info("Did not find 45 elements as expected in titelive"
                        + " line. Skipping line")
            return None

        if (self.lines_checked % SYNC_PART_SIZE) == 0:
            self.logEvent(LocalProviderEventType.SyncPartEnd,
                          self.lines_checked)

        self.infos = get_infos_from_data_line(elements)

        self.extraData = {}

        self.thing_type, self.extraData['bookFormat'] = get_thing_type_and_extra_data_from_titelive_type(
            self.infos['code_support'])

        if self.thing_type is None:
            return None

        self.lines_checked += 1
        providable_info = ProvidableInfo()
        providable_info.type = Product
        providable_info.idAtProviders = self.infos['ean13']
        providable_info.dateModifiedAtProvider = read_things_date(self.infos['date_updated'])
        return providable_info

    def updateObject(self, thing):
        assert thing.idAtProviders == self.infos['ean13']

        thing.name = trim_with_elipsis(self.infos['titre'], 140)
        thing.datePublished = read_things_date(self.infos['date_parution'])
        thing.type = self.thing_type
        thing.extraData = get_extraData_from_infos(self.extraData, self.infos)

        if self.infos['url_extrait_pdf'] != '':
            thing.mediaUrls.append(self.infos['url_extrait_pdf'])


def get_lines_from_thing_file(last_read_lines: int, thing_file: str):
    with open(thing_file, 'r', encoding='iso-8859-1') as f:
        data_lines = islice(f.readlines(), last_read_lines, None)
    return data_lines
