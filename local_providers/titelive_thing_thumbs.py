import os
import re
from datetime import datetime
from pathlib import Path, PurePath
from zipfile import ZipFile

from models.local_provider import LocalProvider, ProvidableInfo
from models.local_provider_event import LocalProviderEventType
from models.thing import Thing
from repository import local_provider_event_queries

DATE_REGEXP = re.compile('livres_tl(\d+).zip')


def file_date(filename_or_zipfile):
    if isinstance(filename_or_zipfile, ZipFile):
        filename = filename_or_zipfile.filename
    else:
        filename = filename_or_zipfile
    match = DATE_REGEXP.search(str(filename))
    if not match:
        raise ValueError('Invalid filename in titelive_works : '
                         + filename)
    return int(match.group(1))


class TiteLiveThingThumbs(LocalProvider):

    help = ""
    identifierDescription = "Pas d'identifiant nécessaire"\
                            + "(on synchronise tout)"
    identifierRegexp = None
    name = "TiteLive (Epagine / Place des libraires.com) Thumbs"
    objectType = Thing
    canCreate = False

    def __init__(self, offerer, **options):
        super().__init__(offerer, **options)
        if 'mock' in options and options['mock']:
            data_root_path = Path(os.path.dirname(os.path.realpath(__file__)))\
                            / '..' / 'sandboxes' / 'providers' / 'titelive_works'
        else:
            data_root_path = Path(os.path.dirname(os.path.realpath(__file__)))\
                            / '..' / 'ftp_mirrors' / 'titelive_works'
        if not os.path.isdir(data_root_path):
            raise ValueError('File not found : '+str(data_root_path)
                             + '\nDid you run "pc ftp_mirrors" ?')
        data_thumbs_path = data_root_path / 'Atoo'
        print(data_thumbs_path)

        all_zips = list(sorted(data_thumbs_path.glob('livres_tl*.zip')))
        latest_sync_part_end_event = local_provider_event_queries.find_latest_sync_part_end_event(self.dbObject)

        if latest_sync_part_end_event is None:
            self.zips = iter(all_zips)
        else:
            self.zips = iter(filter(lambda z: file_date(z) > int(latest_sync_part_end_event.payload),
                                    all_zips))
        self.thumb_zipinfos = None
        self.zip = None

    def open_next_file(self):
        if self.zip:
            self.logEvent(LocalProviderEventType.SyncPartEnd, file_date(self.zip))
        self.zip = ZipFile(str(self.zips.__next__()))
        print("  Importing thumbs from file "+str(self.zip))
        self.logEvent(LocalProviderEventType.SyncPartStart, file_date(self.zip))
        self.thumb_zipinfos = iter(filter(lambda f: f.filename.lower().endswith('.jpg'),
                                          sorted(self.zip.infolist(),
                                                 key=lambda f: f.filename)))

    def __next__(self):
        if self.thumb_zipinfos is None:
            self.open_next_file()
        try:
            self.thumb_zipinfo = self.thumb_zipinfos.__next__()
        except StopIteration:
            self.open_next_file()
            self.thumb_zipinfo = self.thumb_zipinfos.__next__()

        p_info = ProvidableInfo()
        p_info.type = Thing
        p_info.dateModifiedAtProvider = None
        path = PurePath(self.thumb_zipinfo.filename)
        p_info.idAtProviders = path.name.split('_', 1)[0]
        self.thingId = p_info.idAtProviders

        return p_info

    def getObjectThumbDates(self, thing):
        assert thing.idAtProviders == self.thingId
        zdtime = self.thumb_zipinfo.date_time
        if self.thumb_zipinfo.filename.endswith('_1_75.jpg'):
            return [datetime(*zdtime)]
        else:
            return [None, datetime(*zdtime)]

    def getObjectThumb(self, thing, index):
        assert thing.idAtProviders == self.thingId
        expectedIndex = 0 if self.thumb_zipinfo.filename.endswith('_1_75.jpg')\
                        else 1
        assert index == expectedIndex
        with self.zip.open(self.thumb_zipinfo) as f:
            return f.read()
