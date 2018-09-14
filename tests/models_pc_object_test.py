from datetime import datetime

import pytest
from sqlalchemy import Column, DateTime

from models import PcObject
from models.db import Model


class TimeInterval(PcObject, Model):
    start = Column(DateTime)
    end = Column(DateTime)


time_interval = TimeInterval()
time_interval.start = datetime(2018, 1, 1, 10, 20, 30, 111000)
time_interval.end = datetime(2018, 2, 2, 5, 15, 25, 222000)


def test_populate_from_dict_deserializes_datetimes():
    # given
    raw_data = {'start': '2018-03-03T15:25:35.123Z', 'end': '2018-04-04T20:10:30.456Z'}

    # when
    time_interval.populateFromDict(raw_data)

    # then
    assert time_interval.start == datetime(2018, 3, 3, 15, 25, 35, 123000)
    assert time_interval.end == datetime(2018, 4, 4, 20, 10, 30, 456000)


def test_populate_from_dict_deserializes_datetimes_without_milliseconds():
    # given
    raw_data = {'start': '2018-03-03T15:25:35', 'end': '2018-04-04T20:10:30'}

    # when
    time_interval.populateFromDict(raw_data)

    # then
    assert time_interval.start == datetime(2018, 3, 3, 15, 25, 35)
    assert time_interval.end == datetime(2018, 4, 4, 20, 10, 30)


def test_populate_from_dict_deserializes_datetimes_without_milliseconds_with_trailing_z():
    # given
    raw_data = {'start': '2018-03-03T15:25:35Z', 'end': '2018-04-04T20:10:30Z'}

    # when
    time_interval.populateFromDict(raw_data)

    # then
    assert time_interval.start == datetime(2018, 3, 3, 15, 25, 35)
    assert time_interval.end == datetime(2018, 4, 4, 20, 10, 30)


def test_populate_from_dict_raises_type_error_if_raw_date_is_invalid():
    # given
    raw_data = {'start': '2018-03-03T15:25:35.123Z', 'end': 'abcdef'}

    # when
    with pytest.raises(TypeError):
        time_interval.populateFromDict(raw_data)
