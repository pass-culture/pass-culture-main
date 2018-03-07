# -*- coding: utf-8 -*-
import collections
from decimal import Decimal
import json
from pprint import pprint

def listify (query, **kwargs):
    include_joins = kwargs.get('include_joins', [])
    if isinstance(query, collections.Iterable):
        elements = list(map(
            lambda obj: obj._asdict(include_joins=include_joins),
            query
        ))
    else:
        elements = [query._asdict(include_joins=include_joins)]
    return elements

class BytesEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, bytes):
            return obj.decode('ascii')
        elif isinstance(obj, Decimal):
            return str(obj)
        # Let the base class default method raise the TypeErro
        return json.JSONEncoder.default(self, obj)

def printify (elements):
    print(json.dumps(elements, cls=BytesEncoder, indent=2))
