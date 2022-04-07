""" json encoder """
from enum import Enum

from flask.json import JSONEncoder


class EnumJSONEncoder(JSONEncoder):
    def default(self, obj):  # type: ignore [no-untyped-def]
        try:
            if isinstance(obj, Enum):
                return str(obj)
            iterable = iter(obj)
        except TypeError:
            pass
        else:
            return list(iterable)
        return JSONEncoder.default(self, obj)
