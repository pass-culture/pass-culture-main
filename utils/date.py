from datetime import datetime
from babel.dates import get_timezone, format_datetime as babel_format_datetime
from math import floor

from utils.string_processing import parse_timedelta

def format_datetime(dt):
    return babel_format_datetime(dt,
                                 format='long',
                                 locale='fr')[:-9]

def format_duration(dr):
    return floor(parse_timedelta(dr).total_seconds()/60)
