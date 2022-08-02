from datetime import datetime
from pathlib import PurePath
import re

from pcapi.connectors.ftp_titelive import get_files_to_process_from_titelive_ftp
from pcapi.connectors.ftp_titelive import get_zip_file_from_ftp
import pcapi.core.offers.models as offers_models
import pcapi.core.providers.models as providers_models
import pcapi.core.providers.repository as providers_repository
from pcapi.domain.titelive import get_date_from_filename
from pcapi.local_providers.local_provider import LocalProvider
from pcapi.local_providers.providable_info import ProvidableInfo


DATE_REGEXP = re.compile(r"livres_tl(\d+).zip")
THUMB_FOLDER_NAME_TITELIVE = "Atoo"
SYNCHONISABLE_FILE_EXTENSION = "_75.jpg"


class TiteLiveThingThumbs(LocalProvider):
    name = "TiteLive (Epagine / Place des libraires.com) Thumbs"
    can_create = False

    def __init__(self):  # type: ignore [no-untyped-def]
        super().__init__()

        all_zips = get_files_to_process_from_titelive_ftp(THUMB_FOLDER_NAME_TITELIVE, DATE_REGEXP)

        self.zips = self.get_remaining_files_to_check(all_zips)
        self.thumb_zipinfos = None
        self.zip = None

    def __next__(self) -> list[ProvidableInfo]:
        if self.thumb_zipinfos is None:
            self.open_next_file()

        try:
            self.thumb_zipinfo = next(self.thumb_zipinfos)  # type: ignore [arg-type]
        except StopIteration:
            self.open_next_file()
            self.thumb_zipinfo = next(self.thumb_zipinfos)  # type: ignore [arg-type]

        path = PurePath(self.thumb_zipinfo.filename)

        file_identifier = path.name.split("_", 1)[0]
        file_date = datetime(*self.thumb_zipinfo.date_time)
        product_providable_info = self.create_providable_info(
            offers_models.Product, file_identifier, file_date, file_identifier
        )

        return [product_providable_info]

    def open_next_file(self):  # type: ignore [no-untyped-def]
        if self.zip:
            file_date = get_date_from_filename(self.zip, DATE_REGEXP)
            self.log_provider_event(providers_models.LocalProviderEventType.SyncPartEnd, file_date)

        next_zip_file_name = str(next(self.zips))
        file_date = get_date_from_filename(next_zip_file_name, DATE_REGEXP)

        self.zip = get_zip_file_from_ftp(next_zip_file_name, THUMB_FOLDER_NAME_TITELIVE)
        self.log_provider_event(providers_models.LocalProviderEventType.SyncPartStart, file_date)

        self.thumb_zipinfos = iter(
            filter(
                lambda f: f.filename.lower().endswith(SYNCHONISABLE_FILE_EXTENSION),
                sorted(self.zip.infolist(), key=lambda f: f.filename),
            )
        )

    def get_object_thumb_index(self) -> int:
        return extract_thumb_index(self.thumb_zipinfo.filename)

    def get_object_thumb(self) -> bytes:
        with self.zip.open(self.thumb_zipinfo) as f:
            return f.read()

    def get_remaining_files_to_check(self, all_zips):  # type: ignore [no-untyped-def]
        latest_sync_part_end_event = providers_repository.find_latest_sync_part_end_event(self.provider)

        if latest_sync_part_end_event is None:
            return iter(all_zips)
        payload = int(latest_sync_part_end_event.payload)
        return iter(filter(lambda z: get_date_from_filename(z, DATE_REGEXP) > payload, all_zips))

    def fill_object_attributes(self, obj):  # type: ignore [no-untyped-def]
        pass


def extract_thumb_index(filename: str) -> int:
    split_filename = filename.split("_")
    if len(split_filename) > 2:
        return int(split_filename[-2])
    return -1
