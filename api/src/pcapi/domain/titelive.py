from datetime import datetime


TITELIVE_THINGS_DATE_FORMAT = "%d/%m/%Y"
TITELIVE_DESCRIPTION_DATE_FORMAT = "%y%m%d"


def read_things_date(date: str) -> datetime:
    return datetime.strptime(date, TITELIVE_THINGS_DATE_FORMAT)


def parse_things_date_to_string(date: str) -> str:
    return str(read_things_date(date))
