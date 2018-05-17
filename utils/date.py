from datetime import datetime
from babel.dates import get_timezone, format_datetime as babel_format_datetime


def format_datetime(dt):
    return babel_format_datetime(datetime.now(),
                                 format='long',
                                 locale='fr')[:-9]
