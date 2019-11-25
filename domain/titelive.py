from datetime import datetime
from typing import Callable, Pattern
from zipfile import ZipFile

from connectors.api_titelive_stocks import get_titelive_stocks

TITELIVE_THINGS_DATE_FORMAT = "%d/%m/%Y"
TITELIVE_DESCRIPTION_DATE_FORMAT = "%y%m%d"
TITELIVE_STOCK_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


def get_stocks_information(siret: str,
                           last_processed_isbn: str,
                           get_titelive_stocks_from_api: Callable = get_titelive_stocks) -> iter:
    api_response = get_titelive_stocks_from_api(siret, last_processed_isbn)
    return iter(api_response['stocks'])


def read_description_date(date):
    return datetime.strptime(date, TITELIVE_DESCRIPTION_DATE_FORMAT) if date else None


def read_things_date(date):
    return datetime.strptime(date, TITELIVE_THINGS_DATE_FORMAT) if date else None


def read_stock_datetime(date):
    return datetime.strptime(date, TITELIVE_STOCK_DATETIME_FORMAT) if date else None


def put_today_file_at_end_of_list(ordered_files_list, date_regexp):
    today = datetime.utcnow().day
    files_after_today = list(filter(lambda f: get_date_from_filename(f, date_regexp) > today,
                                    ordered_files_list))
    files_before_today = list(filter(lambda f: get_date_from_filename(f, date_regexp) <= today,
                                     ordered_files_list))
    return files_after_today + files_before_today


def get_date_from_filename(filename: str, date_regexp: Pattern) -> int:
    if isinstance(filename, ZipFile):
        real_filename = filename.filename
    else:
        real_filename = filename
    match = date_regexp.search(str(real_filename))
    if not match:
        raise ValueError('Invalid filename in Titelive folder : %s' % filename)
    return int(match.groups()[-1])
