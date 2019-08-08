import enum
from collections import OrderedDict
from datetime import datetime
from functools import singledispatch

import sqlalchemy
from psycopg2._range import DateTimeRange
from sqlalchemy.orm.collections import InstrumentedList

from domain.reimbursement import BookingReimbursement
from models import PcObject
from models.pc_object import _format_into_ISO_8601, _is_human_id_column
from utils.date import DateTimes
from utils.human_ids import humanize


@singledispatch
def as_dict(model, include: dict = None, **options):
    pass


@as_dict.register(BookingReimbursement)
def _(model, include: dict = None, **options):
    dict_booking = as_dict(model.booking, include=include)
    dict_booking['token'] = dict_booking['token'] if dict_booking['isUsed'] else None
    dict_booking['reimbursed_amount'] = model.reimbursed_amount
    dict_booking['reimbursement_rule'] = model.reimbursement.value.description
    return dict_booking


@as_dict.register(PcObject)
def _(model, include: dict = None, **options):
    if include is None:
        include = []

    result = OrderedDict()
    columns = model.__class__.__table__.columns._data
    model_attributes = model.__mapper__.c.keys()

    for key in _remove_excluded_keys(model_attributes):
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

        if isinstance(value, InstrumentedList) \
                or value.__class__.__name__ == 'AppenderBaseQuery' \
                or isinstance(value, list):

            result[key] = list(
                map(
                    lambda attr: as_dict(attr, include=sub_joins),
                    filter(lambda x: not x.is_soft_deleted(), value)
                )
            )

            if resolve is not None:
                result[key] = list(map(lambda v: resolve(v), result[key]))

        elif isinstance(value, PcObject):
            result[key] = as_dict(value, include=sub_joins)
            if resolve is not None:
                result[key] = resolve(result[key])
        else:
            result[key] = serialize(value)

    if options and \
            'resolve' in options and \
            options['resolve']:
        return options['resolve'](result)
    else:
        return result


def _remove_excluded_keys(keys):
    return filter(lambda k: not isinstance(k, str) or (isinstance(k, str) and not k.startswith('-')), keys)


def serialize(value):
    if isinstance(value, sqlalchemy.Enum):
        return value.name
    elif isinstance(value, enum.Enum):
        return value.value
    elif isinstance(value, datetime):
        return _format_into_ISO_8601(value)
    elif isinstance(value, DateTimeRange):
        return {
            'start': value.lower,
            'end': value.upper
        }
    elif isinstance(value, list) \
            and len(value) > 0 \
            and isinstance(value[0], DateTimeRange):
        return list(map(lambda d: {'start': d.lower,
                                   'end': d.upper},
                        value))
    elif isinstance(value, DateTimes):
        return [_format_into_ISO_8601(v) for v in value.datetimes]

    else:
        return value
