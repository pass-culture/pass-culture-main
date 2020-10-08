from collections import OrderedDict
from functools import singledispatch
from typing import Iterable, Set, List

from sqlalchemy.orm.collections import InstrumentedList

from pcapi.domain.reimbursement import BookingReimbursement
from pcapi.models.allocine_venue_provider import AllocineVenueProvider
from pcapi.models.pc_object import PcObject
from pcapi.models.venue_provider import VenueProvider
from pcapi.routes.serialization.serializer import serialize


@singledispatch
def as_dict(value, column=None, includes: Iterable = ()):
    return serialize(value, column=column)


@as_dict.register(BookingReimbursement)
def _(booking_reimbursement, column=None, includes: Iterable = ()):
    dict_booking = as_dict(booking_reimbursement.booking, includes=includes)
    dict_booking['token'] = dict_booking['token'] if dict_booking['isUsed'] else None
    dict_booking['reimbursed_amount'] = booking_reimbursement.reimbursed_amount
    dict_booking['reimbursement_rule'] = booking_reimbursement.reimbursement.description
    return dict_booking


@as_dict.register(InstrumentedList)
def _(models, column=None, includes: Iterable = ()):
    not_deleted_objects = filter(lambda x: not x.is_soft_deleted(), models)
    return [as_dict(o, includes=includes) for o in not_deleted_objects]


@as_dict.register(AllocineVenueProvider)
def _(model, column=None, includes: Iterable = ()):
    result = OrderedDict()

    venue_provider_columns = VenueProvider.__table__.columns._data
    allocine_specific_columns = AllocineVenueProvider.__table__.columns._data
    allocine_venue_provider_columns = OrderedDict(venue_provider_columns.items()
                                                  + allocine_specific_columns.items())

    for key in _keys_to_serialize(model, includes):
        value = getattr(model, key)
        column = allocine_venue_provider_columns.get(key)
        result[key] = as_dict(value, column=column)

    for join in _joins_to_serialize(includes):
        key = join['key']
        sub_includes = join.get('includes', set())
        value = getattr(model, key)
        result[key] = as_dict(value, includes=sub_includes)

    return result


@as_dict.register(PcObject)
def _(model, column=None, includes: Iterable = ()):
    result = OrderedDict()

    for key in _keys_to_serialize(model, includes):
        value = getattr(model, key)
        columns = model.__class__.__table__.columns._data
        column = columns.get(key)
        result[key] = as_dict(value, column=column)

    for join in _joins_to_serialize(includes):
        key = join['key']
        sub_includes = join.get('includes', set())
        value = getattr(model, key)
        result[key] = as_dict(value, includes=sub_includes)

    return result


def _joins_to_serialize(includes: Iterable) -> List[dict]:
    dict_joins = filter(lambda a: isinstance(a, dict), includes)
    return list(dict_joins)


def _keys_to_serialize(model, includes: Iterable) -> Set[str]:
    model_attributes = model.__mapper__.c.keys()
    return set(model_attributes).union(_included_properties(includes)) - _excluded_keys(includes)


def _included_properties(includes: Iterable) -> Set[str]:
    string_keys = filter(lambda a: isinstance(a, str), includes)
    included_keys = filter(lambda a: not a.startswith('-'), string_keys)
    return set(included_keys)


def _excluded_keys(includes):
    string_keys = filter(lambda a: isinstance(a, str), includes)
    excluded_keys = filter(lambda a: a.startswith('-'), string_keys)
    cleaned_keys = map(lambda a: a[1:], excluded_keys)
    return set(cleaned_keys)
