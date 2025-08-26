import typing
from enum import Enum

from flask.json.provider import DefaultJSONProvider


class EnumJSONEncoder(DefaultJSONProvider):
    def default(self, obj: typing.Any) -> typing.Any:
        try:
            if isinstance(obj, Enum):
                return str(obj)
            iterable = iter(obj)
        except TypeError:
            pass
        else:
            return list(iterable)
        return super().default(obj)
