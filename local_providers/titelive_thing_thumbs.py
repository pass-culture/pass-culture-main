import os
import re
from datetime import datetime
from pathlib import Path, PurePath
from zipfile import ZipFile

from io import BytesIO

from models.local_provider import LocalProvider, ProvidableInfo
from models.local_provider_event import LocalProviderEventType
from models.thing import Thing
from repository import local_provider_event_queries
from utils.ftp_titelive import connect_to_titelive_ftp, get_titelive_ftp

DATE_REGEXP = re.compile('livres_tl(\d+).zip')

THUMB_FOLDER_NAME_TITELIVE = 'Atoo'


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


def get_all_zips_from_titelive_ftp():
    ftp_titelive = connect_to_titelive_ftp()
    files_list = ftp_titelive.nlst(THUMB_FOLDER_NAME_TITELIVE)

    files_list_final = [file_name for file_name in files_list if DATE_REGEXP.search(str(file_name))]

    all_thing_files = sorted(files_list_final)
    today = datetime.utcnow().day
    # Titelive 'Quotidien' files stay on the server only for about
    # 26 days. A file with today's date can therefore only be from
    # today, and should always be imported last
    return list(filter(lambda f: file_date(f) > today,
                       all_thing_files)) \
           + list(filter(lambda f: file_date(f) <= today,
                         all_thing_files))


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
        self.is_mock = 'mock' in options and options['mock']
        if self.is_mock:
            data_root_path = Path(os.path.dirname(os.path.realpath(__file__)))\
                            / '..' / 'sandboxes' / 'providers' / 'titelive_works'
            data_thumbs_path = data_root_path / THUMB_FOLDER_NAME_TITELIVE
            print(data_thumbs_path)
            all_zips = list(sorted(data_thumbs_path.glob('livres_tl*.zip')))
        else:
            all_zips = get_all_zips_from_titelive_ftp()

        latest_sync_part_end_event = local_provider_event_queries.find_latest_sync_part_end_event(self.dbObject)

        if latest_sync_part_end_event is None:
            self.zips = iter(all_zips)
        else:
            self.payload = int(latest_sync_part_end_event.payload)
            self.zips = iter(filter(lambda z: file_date(z) > self.payload,
                                    all_zips))
        self.thumb_zipinfos = None
        self.zip = None

    def open_next_file(self):
        if self.zip:
            self.logProviderEvent(LocalProviderEventType.SyncPartEnd, file_date(self.zip))
        next_zip_file_name = str(self.zips.__next__())
        if self.is_mock:
            self.zip = ZipFile(next_zip_file_name)
        else:
            data_file = BytesIO()
            data_file.name = next_zip_file_name
            file_path = 'RETR ' + THUMB_FOLDER_NAME_TITELIVE + '/' + next_zip_file_name
            print("  Downloading file " + file_path)
            get_titelive_ftp().retrbinary(file_path, data_file.write)
            self.zip = ZipFile(data_file, 'r')

        print("  Importing thumbs from file " + str(self.zip))
        self.thumb_zipinfos = iter(filter(lambda f: f.filename.lower().endswith('.jpg'),
                                          sorted(self.zip.infolist(),
                                                 key=lambda f: f.filename)))
        self.logProviderEvent(LocalProviderEventType.SyncPartStart, file_date(self.zip))


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
