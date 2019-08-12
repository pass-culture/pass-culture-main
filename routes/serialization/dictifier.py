from collections import OrderedDict
from functools import singledispatch
from typing import Iterable, Set, List

from sqlalchemy.orm.collections import InstrumentedList

from domain.reimbursement import BookingReimbursement
from models import PcObject
from routes.serialization.serializer import serialize


@singledispatch
def as_dict(value, column=None, include: Iterable = ()):
    return serialize(value, column=column)


@as_dict.register(BookingReimbursement)
def _(model, column=None, include: Iterable = ()):
    dict_booking = as_dict(model.booking, include=include)
    dict_booking['token'] = dict_booking['token'] if dict_booking['isUsed'] else None
    dict_booking['reimbursed_amount'] = model.reimbursed_amount
    dict_booking['reimbursement_rule'] = model.reimbursement.value.description
    return dict_booking


@as_dict.register(InstrumentedList)
def _(model, column=None, include: Iterable = ()):
    not_deleted_objects = filter(lambda x: not x.is_soft_deleted(), model)
    return [as_dict(o, include=include) for o in not_deleted_objects]


@as_dict.register(PcObject)
def _(model, column=None, include: Iterable = ()):
    result = OrderedDict()

    for key in _keys_to_serialize(model, include):
        value = getattr(model, key)
        columns = model.__class__.__table__.columns._data
        column = columns.get(key)
        result[key] = as_dict(value, column=column)

    for join in _joins_to_serialize(include):
        key = join['key']
        sub_joins = join.get('sub_joins', set())
        value = getattr(model, key)
        result[key] = as_dict(value, include=sub_joins)

    result['modelName'] = model.__class__.__name__
    return result


def _joins_to_serialize(include: Iterable) -> List[dict]:
    dict_joins = filter(lambda a: isinstance(a, dict), include)
    return list(dict_joins)


def _keys_to_serialize(model, include: Iterable) -> Set[str]:
    model_attributes = model.__mapper__.c.keys()
    return set(model_attributes).union(_included_properties(include)) - _excluded_keys(include)


def _included_properties(include: Iterable) -> Set[str]:
    string_keys = filter(lambda a: isinstance(a, str), include)
    included_keys = filter(lambda a: not a.startswith('-'), string_keys)
    return set(included_keys)


def _excluded_keys(include):
    string_keys = filter(lambda a: isinstance(a, str), include)
    excluded_keys = filter(lambda a: a.startswith('-'), string_keys)
    cleaned_keys = map(lambda a: a[1:], excluded_keys)
    return set(cleaned_keys)
