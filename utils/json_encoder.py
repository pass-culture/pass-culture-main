""" json encoder """
from flask.json import JSONEncoder
from enum import Enum


class EnumJSONEncoder(JSONEncoder):

    def default(self, obj):
        try:
            if isinstance(obj, Enum):
                return str(obj)
            iterable = iter(obj)
        except TypeError:
            pass
        else:
            return list(iterable)
        return JSONEncoder.default(self, obj)
