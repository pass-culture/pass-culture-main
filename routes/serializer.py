import enum
from collections import OrderedDict
from datetime import datetime
from functools import singledispatch
from pprint import pprint

import sqlalchemy
from psycopg2._range import DateTimeRange
from sqlalchemy.orm.collections import InstrumentedList

from domain.reimbursement import BookingReimbursement
from models import PcObject, Feature
from models.pc_object import _format_into_ISO_8601, _is_human_id_column
from utils.date import DateTimes
from utils.human_ids import humanize


@singledispatch
def as_dict(model, include: dict = None, **options):
    return serialize(model)


@as_dict.register(BookingReimbursement)
def _(model, include: dict = None, **options):
    dict_booking = as_dict(model.booking, include=include)
    dict_booking['token'] = dict_booking['token'] if dict_booking['isUsed'] else None
    dict_booking['reimbursed_amount'] = model.reimbursed_amount
    dict_booking['reimbursement_rule'] = model.reimbursement.value.description
    return dict_booking


@as_dict.register(list)
@as_dict.register(InstrumentedList)
def _(model, include: dict = None, **options):
    not_deleted_objects = list(filter(lambda x: not x.is_soft_deleted(), model))
    result = list(map(lambda attribute: as_dict(attribute,
                                                include=include,
                                                resolve=options['resolve']), not_deleted_objects))
    if options and options['resolve'] is not None:
        return list(map(lambda v: options['resolve'](v), result))
    return result


@as_dict.register(PcObject)
def _(model, include: dict = None, **options):
    if include is None:
        include = []

    result = OrderedDict()
    columns = model.__class__.__table__.columns._data
    model_attributes = model.__mapper__.c.keys()

    for key in model_attributes:
        is_key_to_exclude = '-' + key in include
        if is_key_to_exclude:
            continue

        value = getattr(model, key)

        column = columns.get(key)
        is_human_id_column = column is not None and _is_human_id_column(column)

        if is_human_id_column:
            result[key] = humanize(value)
        elif key == 'firstThumbDominantColor' and value:
            result[key] = list(value)
        else:
            result[key] = serialize(value)

    # add the model name
    result['modelName'] = model.__class__.__name__
    # TODO: for feature model add nameKey
    if isinstance(model, Feature):
        result['nameKey'] = str(model.name).replace('FeatureToggle.', '')

    for join in _remove_excluded_keys(include):
        if isinstance(join, dict):
            key = join['key']
            resolve = join.get('resolve')
            sub_joins = join.get('sub_joins')
        else:
            key = join
            resolve = None
            sub_joins = None

        value = getattr(model, key)
        if value is None:
            continue

        # TODO: if value.__class__.__name__ == 'AppenderBaseQuery':
        result[key] = as_dict(value, include=sub_joins, resolve=resolve)
        if resolve is not None:
            pprint(key)
            pprint(result[key])
            try:
                result[key] = resolve(result[key])
            except TypeError:
                result[key] = map(lambda v: resolve(v), result[key])

    return result


def _remove_excluded_keys(keys):
    return filter(lambda k: not isinstance(k, str) or (isinstance(k, str) and not k.startswith('-')), keys)


@singledispatch
def serialize(value):
    return value


@serialize.register(sqlalchemy.Enum)
def _(value):
    return value.name


@serialize.register(enum.Enum)
def _(value):
    return value.value


@serialize.register(datetime)
def _(value):
    return _format_into_ISO_8601(value)


@serialize.register(DateTimeRange)
def _(value):
    return {
        'start': value.lower,
        'end': value.upper
    }


@serialize.register(list)
def _(value):
    return list(map(lambda d: serialize(d), value))


@serialize.register(DateTimes)
def _(value):
    return [_format_into_ISO_8601(v) for v in value.datetimes]
