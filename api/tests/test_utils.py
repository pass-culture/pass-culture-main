import datetime
import enum
import operator
import uuid


def fake(object_type):
    class FakeObject(object_type):
        def __eq__(self, other_object):
            return isinstance(other_object, object_type)

    return FakeObject()


def json_default(data):
    conversions = {
        enum.Enum: operator.attrgetter("value"),
        datetime.datetime: str,
        uuid.UUID: str,
    }
    for type_, func in conversions.items():
        if isinstance(data, type_):
            return func(data)

    return data
