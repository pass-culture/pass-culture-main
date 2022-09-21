import datetime
import enum

from pcapi.routes.serialization.serializer import serialize


def test_serialize_datetime():
    d = datetime.datetime(2022, 1, 1, 12, 34, 56)
    assert serialize(d) == "2022-01-01T12:34:56Z"


def test_serialize_enum():
    class EnumTest(enum.Enum):
        TEST = {"str": "tata", "bool": False, "list": ["toto", "tata"]}

    enum_ = EnumTest.TEST
    assert serialize(enum_) == enum_.value
