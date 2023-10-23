from datetime import datetime
from typing import Pattern
from zipfile import ZipFile


TITELIVE_THINGS_DATE_FORMAT = "%d/%m/%Y"
TITELIVE_DESCRIPTION_DATE_FORMAT = "%y%m%d"


def read_description_date(date: str | None) -> datetime | None:
    return datetime.strptime(date, TITELIVE_DESCRIPTION_DATE_FORMAT) if date else None


def read_things_date(date):  # type: ignore [no-untyped-def]
    return datetime.strptime(date, TITELIVE_THINGS_DATE_FORMAT) if date else None


def put_today_file_at_end_of_list(ordered_files_list: list[str], date_regexp: Pattern[str]) -> list[str]:
    today = datetime.utcnow().day
    files_after_today = list(filter(lambda f: get_date_from_filename(f, date_regexp) > today, ordered_files_list))
    files_before_today = list(filter(lambda f: get_date_from_filename(f, date_regexp) <= today, ordered_files_list))
    return files_after_today + files_before_today


def get_date_from_filename(filename: str, date_regexp: Pattern[str]) -> int:
    if isinstance(filename, ZipFile):
        real_filename = filename.filename
    else:
        real_filename = filename
    match = date_regexp.search(str(real_filename))
    if not match:
        raise ValueError("Invalid filename in Titelive folder : %s" % filename)
    return int(match.groups()[-1])
