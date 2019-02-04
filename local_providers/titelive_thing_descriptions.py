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

DATE_FORMAT = "%y%m%d"
DATE_REGEXP = re.compile('Resume(\d{6}).zip')

DESCRIPTION_FOLDER_NAME_TITELIVE = 'ResumesLivres'


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


def read_date(date):
    return datetime.strptime(str(date), DATE_FORMAT)


def get_all_zips_from_titelive_ftp():
    ftp_titelive = connect_to_titelive_ftp()
    files_list = ftp_titelive.nlst(DESCRIPTION_FOLDER_NAME_TITELIVE)

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


class TiteLiveThingDescriptions(LocalProvider):

    help = ""
    identifierDescription = "Pas d'identifiant nécessaire"\
                            + "(on synchronise tout)"
    identifierRegexp = None
    name = "TiteLive (Epagine / Place des libraires.com) Descriptions"
    objectType = Thing
    canCreate = False

    def __init__(self, offerer, **options):
        super().__init__(offerer, **options)
        self.is_mock = 'mock' in options and options['mock']
        if self.is_mock:
            data_root_path = Path(os.path.dirname(os.path.realpath(__file__))) \
                             / '..' / 'sandboxes' / 'providers' / 'titelive_works'
            data_thumbs_path = data_root_path / DESCRIPTION_FOLDER_NAME_TITELIVE
            print(data_thumbs_path)
            all_zips = list(sorted(data_thumbs_path.glob('Resume*.zip')))
        else:
            all_zips = get_all_zips_from_titelive_ftp()

        latest_sync_part_end_event = local_provider_event_queries.find_latest_sync_part_end_event(self.dbObject)

        if latest_sync_part_end_event is None:
            self.zips = iter(all_zips)
        else:
            self.zips = iter(filter(lambda z: file_date(z) > int(latest_sync_part_end_event.payload),
                                    all_zips))
        self.desc_zipinfos = None
        self.zip = None
        self.dateModified = None

    def open_next_file(self):
        if self.zip:
            self.logEvent(LocalProviderEventType.SyncPartEnd, file_date(self.zip))

        next_zip_file_name = str(self.zips.__next__())
        if self.is_mock:
            self.zip = ZipFile(next_zip_file_name)
        else:
            data_file = BytesIO()
            data_file.name = next_zip_file_name
            file_path = 'RETR ' + DESCRIPTION_FOLDER_NAME_TITELIVE + '/' + next_zip_file_name
            print("  Downloading file " + file_path)
            get_titelive_ftp().retrbinary(file_path, data_file.write)
            self.zip = ZipFile(data_file, 'r')

        print("  Importing descriptions from file "+self.zip.filename)
        self.desc_zipinfos = iter(filter(lambda f: f.filename.lower().endswith('_p.txt'),
                                         sorted(self.zip.infolist(),
                                                key=lambda f: f.filename)))
        self.logEvent(LocalProviderEventType.SyncPartStart, file_date(self.zip))
        desc_filenames = filter(lambda f: f.filename.lower()
                                                    .endswith('_p.txt'),
                                self.zip.infolist())
        self.desc_zipinfos = iter(desc_filenames)
        self.dateModified = read_date(file_date(self.zip))


    def __next__(self):
        if self.desc_zipinfos is None:
            self.open_next_file()
        try:
            self.desc_zipinfo = self.desc_zipinfos.__next__()
        except StopIteration:
            self.open_next_file()
            self.desc_zipinfo = self.desc_zipinfos.__next__()

        p_info = ProvidableInfo()
        p_info.type = Thing
        p_info.dateModifiedAtProvider = self.dateModified
        path = PurePath(self.desc_zipinfo.filename)
        p_info.idAtProviders = path.name.split('_', 1)[0]
        self.thingId = p_info.idAtProviders

        return p_info

    def updateObject(self, thing):
        with self.zip.open(self.desc_zipinfo) as f:
            thing.description = f.read().decode('iso-8859-1')
