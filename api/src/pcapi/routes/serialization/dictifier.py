from collections import OrderedDict
from functools import singledispatch
from typing import Iterable

from sqlalchemy.orm.collections import InstrumentedList

from pcapi.models.pc_object import PcObject
from pcapi.routes.serialization.serializer import serialize


@singledispatch
def as_dict(value, column=None, includes: Iterable = ()):  # type: ignore [no-untyped-def]
    return serialize(value, column=column)


@as_dict.register(InstrumentedList)
def _(models, column=None, includes: Iterable = ()):  # type: ignore [no-untyped-def]
    not_deleted_objects = filter(lambda x: not x.is_soft_deleted(), models)
    return [as_dict(o, includes=includes) for o in not_deleted_objects]


@as_dict.register(PcObject)
def _(model, column=None, includes: Iterable = ()):  # type: ignore [no-untyped-def]
    result = OrderedDict()

    for key in _keys_to_serialize(model, includes):
        value = getattr(model, key)
        columns = model.__mapper__.column_attrs
        column = columns.get(key)
        result[key] = as_dict(value, column=column)

    for join in _joins_to_serialize(includes):
        key = join["key"]
        sub_includes = join.get("includes", set())
        value = getattr(model, key)
        result[key] = as_dict(value, includes=sub_includes)

    return result


def _joins_to_serialize(includes: Iterable) -> list[dict]:
    dict_joins = filter(lambda a: isinstance(a, dict), includes)
    return list(dict_joins)


def _keys_to_serialize(model, includes: Iterable) -> set[str]:  # type: ignore [no-untyped-def]
    model_attributes = model.__mapper__.c.keys()
    return set(model_attributes).union(_included_properties(includes)) - _excluded_keys(includes)


def _included_properties(includes: Iterable) -> set[str]:
    string_keys = filter(lambda a: isinstance(a, str), includes)
    included_keys = filter(lambda a: not a.startswith("-"), string_keys)
    return set(included_keys)


def _excluded_keys(includes):  # type: ignore [no-untyped-def]
    string_keys = filter(lambda a: isinstance(a, str), includes)
    excluded_keys = filter(lambda a: a.startswith("-"), string_keys)
    cleaned_keys = map(lambda a: a[1:], excluded_keys)
    return set(cleaned_keys)
