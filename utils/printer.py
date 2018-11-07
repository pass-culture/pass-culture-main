""" printer """
# -*- coding: utf-8 -*-
import collections
import json
from decimal import Decimal

import models
from utils import includes
from utils.inflect_engine import inflect_engine
from utils.string_processing import get_camel_string


def listify (query, include, resolve=None, **kwargs):
    if resolve is None:
        resolve = lambda obj: obj
    if isinstance(query, collections.Iterable):
        elements = [resolve(obj._asdict(include=include, **kwargs)) for obj in query]
    else:
        elements = [resolve(query._asdict(include=include, **kwargs))]
    return elements

# helpful
""" magic call like get('stocks', Stock.price > 10, lambda obj: obj['id']) """
def get(collection_name, filter = None, resolve = None, **kwargs):
    if resolve is None:
        resolve = lambda obj: obj
    model_name = get_camel_string(inflect_engine.singular_noun(collection_name, 1))
    model = getattr(models, model_name[0].upper() + model_name[1:])
    query = model.query.filter() if filter is None else model.query.filter(filter)
    include = getattr(includes, model_name[0].upper() + model_name[1:] + '_INCLUDES')
    return listify(query, include, resolve, **kwargs)
    #[resolve(obj._asdict(include=include, **kwargs)) for obj in query]

class BytesEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, bytes):
            return obj.decode('ascii')
        elif isinstance(obj, Decimal):
            return str(obj)
        # Let the base class default method raise the TypeErro
        return json.JSONEncoder.default(self, obj)

"""printify(app.get('recommendations', None, get_content, cut=10)[0])"""
def printify (elements):
    print(json.dumps(elements, cls=BytesEncoder, indent=2))
