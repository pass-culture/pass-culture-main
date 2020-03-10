# coding=utf-8
import re
from datetime import datetime, timedelta
from operator import itemgetter

from babel.numbers import format_decimal as babel_format_decimal
from dateparser import parse
from nltk import edit_distance
from psycopg2.extras import DateTimeRange

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
    return inflect_engine.plural(obj.__class__.__name__.lower())


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


def get_date_time_range(date_string, schedule_string, duration_string):
    # DETERMINE DAY MONTH YEAR
    match = re.match(from_to_regex, date_string)
    if match is not None:
        matches = match.group(1, 2, 3, 4)
        if all(matches):
            month = matches[2]
            year = matches[3]
            day_strings = [
                year + '-' + parse_datetime(month, date_formats=['%B']).strftime('%m') + '-' + str(day) for day in
                range(
                    int(matches[0]), int(matches[1])
                )
            ]
    else:
        day_string = parse_datetime(date_string, date_formats=['%E %dd %B %Y'])
        if day_string is not None:
            day_strings = [
                day_string.strftime(DAY_FORMAT)
            ]
    # DETERMINE START AND END SCHEDULE
    end_hour_string = None
    if 'et' in schedule_string:
        return [DateTimeRange()]
    if '-' in schedule_string:
        (start_hour_string, end_hour_string) = schedule_string.split('-')
        format_end_hour_string = get_format_timedelta_string(end_hour_string)
    else:
        start_hour_string = schedule_string
    format_start_hour_string = get_format_timedelta_string(start_hour_string)
    # DETERMINE DURATION
    duration = parse_timedelta(duration_string)
    # CONCAT
    date_time_ranges = [None] * (len(day_strings))
    for (index, day_string) in list(enumerate(day_strings)):
        start_date_string = day_string + 'T' + format_start_hour_string + 'Z'
        start_date = read_date(start_date_string)
        if end_hour_string is not None:
            end_date_string = day_string + 'T' + format_end_hour_string + 'Z'
            end_date = read_date(end_date_string)
        else:
            end_date = start_date + duration
        date_time_ranges[index] = DateTimeRange(start_date, end_date)
    # RETURN
    return date_time_ranges


def get_matched_string_index(target_string, strings):
    distances = map(lambda string: edit_distance(string, target_string), strings)
    return min(enumerate(distances), key=itemgetter(1))[0]


def get_price_value(price_string):
    if isinstance(price_string, int):
        return price_string
    value_string = price_string
    if '€' in value_string:
        value_string = price_string.split('€')[0]
    if value_string.isdigit():
        return int(value_string)
    else:
        return 0


def get_camel_string(string):
    return ''.join(word.capitalize() for word in string.split('_'))


def tokenize_for_search(string):
    return re.split('[^0-9a-zÀ-ÿ]+', string.lower())


def remove_single_letters_for_search(array_of_keywords):
    return list(filter(lambda k: len(k) > 1, array_of_keywords))


def format_decimal(dec):
    return babel_format_decimal(dec, locale='fr_FR')


def pluralize(number_of_occurence: int, word: str) -> str:
    return f'{word}s' if number_of_occurence > 1 else word
