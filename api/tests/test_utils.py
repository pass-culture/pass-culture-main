import datetime
import enum
import operator
import uuid


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
