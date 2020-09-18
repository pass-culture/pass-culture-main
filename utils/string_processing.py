import re
from datetime import datetime, timedelta

from dateparser import parse

from utils.inflect_engine import inflect_engine

DAY_FORMAT = "%Y-%m-%d"
SCHEDULE_FORMAT = "%H:%M:%S.%f"
DATE_FORMAT = DAY_FORMAT + "T" + SCHEDULE_FORMAT + "Z"

from_to_regex = re.compile(r'(\d+)\sau\s(\d+)\s(.*)\s(\d{4})')

schedules = [
    {
        "name": "hours",
        "sep": 'h'
    },
    {
        "name": "minutes",
        "sep": "m",
    },
    {
        "name": "seconds",
        "sep": "s"
    }
]


def get_model_plural_name(obj):
    return inflect_engine.plural(obj.__tablename__.lower())


def dashify(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


# from a typical 10h33, 19h, 17h45m33s...
def parse_timedelta(string):
    cut_string = string.lower()
    config = {}
    for schedule in schedules:
        name = schedule['name']
        sep = schedule['sep']
        if sep in cut_string:
            chunks = cut_string.split(sep)
            if not chunks[0].isdigit():
                break;
            config[name] = int(chunks[0])
            cut_string = sep.join(chunks[1:])
        elif len(cut_string) > 0 and cut_string.isdigit():
            config[name] = int(cut_string)
            break
    return timedelta(**config)


def get_format_timedelta_string(string):
    today_date = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
    schedule_date = today_date + parse_timedelta(string)
    return schedule_date.strftime(SCHEDULE_FORMAT)


def parse_datetime(string, **kwargs):
    return parse(string, languages=['fr'], **kwargs)


def read_date(date_string):
    # remove centiseconds if they are not here
    date_format = DATE_FORMAT if '.' in date_string else DATE_FORMAT.split('.')[0] + "Z"
    return datetime.strptime(date_string, date_format)


def trim_with_elipsis(string, length):
    length_wo_elipsis = length - 1
    return string[:length_wo_elipsis] + (string[length_wo_elipsis:] and '…')


def get_camel_string(string):
    return ''.join(word.capitalize() for word in string.split('_'))


def tokenize_for_search(string):
    return re.split('[^0-9a-zÀ-ÿ]+', string.lower())


def remove_single_letters_for_search(array_of_keywords):
    return list(filter(lambda k: len(k) > 1, array_of_keywords))
