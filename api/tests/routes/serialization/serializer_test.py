import datetime
import enum

from pcapi.routes.serialization.serializer import serialize
from pcapi.utils.date import DateTimes


def test_serialize_custom_datetimes_class():
    assert serialize(DateTimes()) == []  # pylint: disable=use-implicit-booleaness-not-comparison
    d = datetime.datetime(2022, 1, 1, 12, 34, 56)
    assert serialize(DateTimes(d)) == ["2022-01-01T12:34:56Z"]


def test_serialize_enum():
    class EnumTest(enum.Enum):
        TEST = {"str": "tata", "bool": False, "list": ["toto", "tata"]}

    enum_ = EnumTest.TEST
    assert serialize(enum_) == enum_.value
