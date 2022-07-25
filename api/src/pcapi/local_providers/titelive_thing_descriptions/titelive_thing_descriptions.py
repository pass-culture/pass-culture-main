from pathlib import PurePath
import re

from pcapi.connectors.ftp_titelive import get_files_to_process_from_titelive_ftp
from pcapi.connectors.ftp_titelive import get_zip_file_from_ftp
import pcapi.core.offers.models as offers_models
import pcapi.core.providers.models as providers_models
from pcapi.domain.titelive import get_date_from_filename
from pcapi.domain.titelive import read_description_date
from pcapi.local_providers.local_provider import LocalProvider
from pcapi.local_providers.providable_info import ProvidableInfo
from pcapi.repository import local_provider_event_queries


DATE_REGEXP = re.compile(r"Resume(\d{6}).zip")
DESCRIPTION_FOLDER_NAME_TITELIVE = "ResumesLivres"
END_FILE_IDENTIFIER = "_p.txt"


class TiteLiveThingDescriptions(LocalProvider):
    name = "TiteLive (Epagine / Place des libraires.com) Descriptions"
    can_create = False

    def __init__(self):  # type: ignore [no-untyped-def]
        super().__init__()

        all_zips = get_files_to_process_from_titelive_ftp(DESCRIPTION_FOLDER_NAME_TITELIVE, DATE_REGEXP)

        self.zips = self.get_remaining_files_to_check(all_zips)
        self.description_zip_infos = None
        self.zip_file = None
        self.date_modified = None

    def __next__(self) -> list[ProvidableInfo]:
        if self.description_zip_infos is None:
            self.open_next_file()

        try:
            self.description_zip_info = next(self.description_zip_infos)  # type: ignore [arg-type]
        except StopIteration:
            self.open_next_file()
            self.description_zip_info = next(self.description_zip_infos)  # type: ignore [arg-type]

        path = PurePath(self.description_zip_info.filename)
        date_from_filename = path.name.split("_", 1)[0]
        product_providable_info = self.create_providable_info(
            offers_models.Product, date_from_filename, self.date_modified, date_from_filename
        )
        return [product_providable_info]

    def fill_object_attributes(self, product: offers_models.Product):  # type: ignore [no-untyped-def]
        with self.zip_file.open(self.description_zip_info) as f:
            description = f.read().decode("iso-8859-1")
        product.description = description.replace("\x00", "")

    def open_next_file(self):  # type: ignore [no-untyped-def]
        if self.zip_file:
            current_file_date = get_date_from_filename(self.zip_file, DATE_REGEXP)
            self.log_provider_event(providers_models.LocalProviderEventType.SyncPartEnd, current_file_date)
        next_zip_file_name = str(next(self.zips))
        self.zip_file = get_zip_file_from_ftp(next_zip_file_name, DESCRIPTION_FOLDER_NAME_TITELIVE)
        new_file_date = get_date_from_filename(self.zip_file, DATE_REGEXP)

        self.log_provider_event(providers_models.LocalProviderEventType.SyncPartStart, new_file_date)

        self.description_zip_infos = self.get_description_files_from_zip_info()

        self.date_modified = read_description_date(str(new_file_date))

    def get_remaining_files_to_check(self, all_zips) -> iter:  # type: ignore [no-untyped-def, valid-type]
        latest_sync_part_end_event = local_provider_event_queries.find_latest_sync_part_end_event(self.provider)

        if latest_sync_part_end_event is None:
            return iter(all_zips)
        return iter(
            filter(lambda z: get_date_from_filename(z, DATE_REGEXP) > int(latest_sync_part_end_event.payload), all_zips)  # type: ignore [arg-type]
        )

    def get_description_files_from_zip_info(self) -> iter:  # type: ignore [valid-type]
        sorted_files = sorted(self.zip_file.infolist(), key=lambda f: f.filename)
        filtered_files = filter(lambda f: f.filename.lower().endswith(END_FILE_IDENTIFIER), sorted_files)
        return iter(filtered_files)
