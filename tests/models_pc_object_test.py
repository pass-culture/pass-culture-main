from datetime import datetime, timedelta

import pytest
from sqlalchemy import Column, DateTime

from models import PcObject, Offer, EventOccurrence
from models.db import Model
from models.pc_object import serialize


class TimeInterval(PcObject, Model):
    start = Column(DateTime)
    end = Column(DateTime)


time_interval = TimeInterval()
time_interval.start = datetime(2018, 1, 1, 10, 20, 30, 111000)
time_interval.end = datetime(2018, 2, 2, 5, 15, 25, 222000)
now = datetime.utcnow()


@pytest.mark.standalone
def assert_is_in_ISO_8601_format(date_text):
    try:
        format_string = '%Y-%m-%dT%H:%M:%S.%fZ'
        datetime.strptime(date_text, format_string)
    except TypeError:
        assert False, 'La date doit être un str'
    except ValueError:
        assert False, 'La date doit être au format ISO 8601 %Y-%m-%dT%H:%M:%S.%fZ'


@pytest.mark.standalone
def test_populate_from_dict_deserializes_datetimes():
    # given
    raw_data = {'start': '2018-03-03T15:25:35.123Z', 'end': '2018-04-04T20:10:30.456Z'}

    # when
    time_interval.populateFromDict(raw_data)

    # then
    assert time_interval.start == datetime(2018, 3, 3, 15, 25, 35, 123000)
    assert time_interval.end == datetime(2018, 4, 4, 20, 10, 30, 456000)


@pytest.mark.standalone
def test_populate_from_dict_deserializes_datetimes_without_milliseconds():
    # given
    raw_data = {'start': '2018-03-03T15:25:35', 'end': '2018-04-04T20:10:30'}

    # when
    time_interval.populateFromDict(raw_data)

    # then
    assert time_interval.start == datetime(2018, 3, 3, 15, 25, 35)
    assert time_interval.end == datetime(2018, 4, 4, 20, 10, 30)


@pytest.mark.standalone
def test_populate_from_dict_deserializes_datetimes_without_milliseconds_with_trailing_z():
    # given
    raw_data = {'start': '2018-03-03T15:25:35Z', 'end': '2018-04-04T20:10:30Z'}

    # when
    time_interval.populateFromDict(raw_data)

    # then
    assert time_interval.start == datetime(2018, 3, 3, 15, 25, 35)
    assert time_interval.end == datetime(2018, 4, 4, 20, 10, 30)


@pytest.mark.standalone
def test_populate_from_dict_raises_type_error_if_raw_date_is_invalid():
    # given
    raw_data = {'start': '2018-03-03T15:25:35.123Z', 'end': 'abcdef'}

    # when
    with pytest.raises(TypeError):
        time_interval.populateFromDict(raw_data)


@pytest.mark.standalone
def test_serialize_on_datetime_list_returns_string_with_date_in_ISO_8601_list():
    # Given
    eventOccurrence = EventOccurrence()
    eventOccurrence.beginningDatetime = now
    eventOccurrence.endDatetime = now + timedelta(hours=3)
    offer = Offer()
    offer.eventOccurrences = [eventOccurrence]
    # When
    serialized_list = serialize(offer.dateRange)
    # Then
    for datetime in serialized_list:
        assert_is_in_ISO_8601_format(datetime)
