""" pc_object """
import enum
import re
import traceback
import uuid
from collections import OrderedDict
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pprint import pprint
from typing import List, Any, Iterable, Set

import sqlalchemy
from psycopg2.extras import DateTimeRange
from sqlalchemy import CHAR, \
    BigInteger, \
    Column, \
    Float, \
    Integer, \
    Numeric, \
    String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.exc import DataError, IntegrityError, InternalError
from sqlalchemy.orm.collections import InstrumentedList

from models.api_errors import ApiErrors, \
                              DecimalCastError, \
                              DateTimeCastError, \
                              UuidCastError
from models.db import db, Model
from models.soft_deletable_mixin import SoftDeletableMixin
from utils.date import match_format, DateTimes
from utils.human_ids import dehumanize, humanize, NonDehumanizableId
from utils.logger import logger

DUPLICATE_KEY_ERROR_CODE = '23505'
NOT_FOUND_KEY_ERROR_CODE = '23503'
OBLIGATORY_FIELD_ERROR_CODE = '23502'


class DeletedRecordException(Exception):
    pass


class PcObject:
    id = Column(BigInteger,
                primary_key=True,
                autoincrement=True)

    def __init__(self, **options):
        from_dict = options.get('from_dict')
        if from_dict:
            self.populate_from_dict(from_dict)

    def __repr__(self):
        id = "unsaved" \
            if self.id is None \
            else str(self.id) + "/" + humanize(self.id)
        return '<%s #%s>' % (self.__class__.__name__,
                             id)

    def as_dict(self, **options):
        result = OrderedDict()
        columns = self.__class__.__table__.columns._data
        for key in self.__mapper__.c.keys():
            value = getattr(self, key)

            if options \
                    and 'include' in options \
                    and options.get('include') \
                    and "-" + key in options['include']:
                continue
            column = columns[key]
            is_human_id_column = _is_human_id_column(column)
            if options and options.get('cut'):
                if isinstance(value, str):
                    if len(value) > options['cut']:
                        value = value[:options['cut']] + '...'
            if is_human_id_column:
                result[key] = humanize(value)
                if options \
                        and 'dehumanize' in options \
                        and options['dehumanize']:
                    result['dehumanized' + key[0].capitalize() + key[1:]] = value
            elif key == 'firstThumbDominantColor' and value:
                result[key] = list(value)
            else:
                result[key] = serialize(value)
        # add the model name
        result['modelName'] = self.__class__.__name__
        if options \
                and 'include' in options \
                and options['include']:
            for join in options['include']:
                if isinstance(join, str) and \
                        join.startswith('-'):
                    continue
                elif isinstance(join, dict):
                    key = join['key']
                    refine = join.get('refine')
                    resolve = join.get('resolve')
                    sub_joins = join.get('sub_joins')
                else:
                    key = join
                    refine = None
                    resolve = None
                    sub_joins = None
                try:
                    value = getattr(self, key)
                except AttributeError:
                    continue
                if callable(value):
                    value = value()
                if value is not None:
                    if isinstance(value, InstrumentedList) \
                            or value.__class__.__name__ == 'AppenderBaseQuery' \
                            or isinstance(value, list):
                        if refine is None:
                            final_value = value
                        else:
                            final_value = refine(value, options.get('filters', {}))
                        final_value = filter(lambda x: not x.is_soft_deleted(), final_value)
                        result[key] = list(
                            map(
                                lambda attr: attr.as_dict(
                                    cut=options and options.get('cut'),
                                    include=sub_joins,
                                ),
                                final_value
                            )
                        )
                        if resolve != None:
                            result[key] = list(map(lambda v: resolve(v, options.get('filters', {})),
                                                   result[key]))
                    elif isinstance(value, PcObject):
                        result[key] = value.as_dict(
                            include=sub_joins,
                            cut=options and options.get('cut'),
                        )
                        if resolve != None:
                            result[key] = resolve(result[key], options.get('filters', {}))
                    else:
                        result[key] = serialize(value)

        if options and \
                'resolve' in options and \
                options['resolve']:
            return options['resolve'](result, options.get('filters', {}))
        else:
            return result

    def dump(self):
        pprint(vars(self))

    def populate_from_dict(self, data: dict, skipped_keys: List[str] = []):
        self._check_not_soft_deleted()
        columns = self.__class__.__table__.columns._data
        keys_to_populate = self._get_keys_to_populate(columns, data, skipped_keys)

        for key in keys_to_populate:
            column = columns[key]
            value = _dehumanize_if_needed(column, data.get(key))
            if isinstance(value, str):
                if isinstance(column.type, Integer):
                    self._try_to_set_attribute_with_decimal_value(column, key, value, 'integer')
                elif isinstance(column.type, Float) or isinstance(column.type, Numeric):
                    self._try_to_set_attribute_with_decimal_value(column, key, value, 'float')
                elif isinstance(column.type, String):
                    setattr(self, key, value.strip() if value else value)
                elif isinstance(column.type, DateTime):
                    self._try_to_set_attribute_with_deserialized_datetime(column, key, value)
                elif isinstance(column.type, UUID):
                    self._try_to_set_attribute_with_uuid(column, key, value)
            elif not isinstance(value, datetime) and isinstance(column.type, DateTime):
                self._try_to_set_attribute_with_deserialized_datetime(column, key, value)
            else:
                setattr(self, key, value)

    def errors(self):
        api_errors = ApiErrors()
        columns = self.__class__.__table__.columns._data
        for key in columns.keys():
            column = columns[key]
            value = getattr(self, key)
            if not isinstance(column, Column):
                continue
            if not column.nullable \
                    and not column.foreign_keys \
                    and not column.primary_key \
                    and column.default is None \
                    and value is None:
                api_errors.addError(key, 'Cette information est obligatoire')
            if value is None:
                continue
            if (isinstance(column.type, String) or isinstance(column.type, CHAR)) \
                    and not isinstance(column.type, sqlalchemy.Enum) \
                    and not isinstance(value, str):
                api_errors.addError(key, 'doit être une chaîne de caractères')
            if (isinstance(column.type, String) or isinstance(column.type, CHAR)) \
                    and isinstance(value, str) \
                    and column.type.length \
                    and len(value) > column.type.length:
                api_errors.addError(key,
                                    'Vous devez saisir moins de '
                                    + str(column.type.length)
                                    + ' caractères')
            if isinstance(column.type, Integer) \
                    and not isinstance(value, int):
                api_errors.addError(key, 'doit être un entier')
            if isinstance(column.type, Float) \
                    and not isinstance(value, float):
                api_errors.addError(key, 'doit être un nombre')
        return api_errors

    def is_soft_deleted(self):
        return issubclass(type(self), SoftDeletableMixin) and self.isSoftDeleted

    def soft_delete(self):
        self.deleted = True
        db.session.add(self)

    @staticmethod
    def restize_global_error(e):
        logger.error("UNHANDLED ERROR : ")
        traceback.print_exc()
        return ["global",
                "Une erreur technique s'est produite. Elle a été notée, et nous allons investiguer au plus vite."]

    @staticmethod
    def restize_data_error(e):
        if e.args and len(e.args) > 0 and e.args[0].startswith('(psycopg2.DataError) value too long for type'):
            max_length = re.search('\(psycopg2.DataError\) value too long for type (.*?) varying\((.*?)\)', e.args[0],
                                   re.IGNORECASE).group(2)
            return ['global', "La valeur d'une entrée est trop longue (max " + max_length + ")"]
        else:
            return PcObject.restize_global_error(e)

    @staticmethod
    def restize_integrity_error(e):
        if hasattr(e, 'orig') and hasattr(e.orig, 'pgcode') and e.orig.pgcode == DUPLICATE_KEY_ERROR_CODE:
            field = re.search('Key \((.*?)\)=', str(e._message), re.IGNORECASE).group(1)
            return [field, 'Une entrée avec cet identifiant existe déjà dans notre base de données']
        elif hasattr(e, 'orig') and hasattr(e.orig, 'pgcode') and e.orig.pgcode == NOT_FOUND_KEY_ERROR_CODE:
            field = re.search('Key \((.*?)\)=', str(e._message), re.IGNORECASE).group(1)
            return [field, 'Aucun objet ne correspond à cet identifiant dans notre base de données']
        elif hasattr(e, 'orig') and hasattr(e.orig, 'pgcode') and e.orig.pgcode == OBLIGATORY_FIELD_ERROR_CODE:
            field = re.search('column "(.*?)"', e.orig.pgerror, re.IGNORECASE).group(1)
            return [field, 'Ce champ est obligatoire']
        else:
            return PcObject.restize_global_error(e)

    @staticmethod
    def restize_internal_error(e):
        return PcObject.restize_global_error(e)

    @staticmethod
    def restize_type_error(e):
        if e.args and len(e.args) > 1 and e.args[1] == 'geography':
            return [e.args[2], 'doit etre une liste de nombre décimaux comme par exemple : [2.22, 3.22]']
        elif e.args and len(e.args) > 1 and e.args[1] and e.args[1] == 'decimal':
            return [e.args[2], 'doit être un nombre décimal']
        elif e.args and len(e.args) > 1 and e.args[1] and e.args[1] == 'integer':
            return [e.args[2], 'doit être un entier']
        else:
            return PcObject.restize_global_error(e)

    @staticmethod
    def restize_value_error(e):
        if len(e.args) > 1 and e.args[1] == 'enum':
            return [e.args[2], ' doit etre dans cette liste : ' + ",".join(map(lambda x: '"' + x + '"', e.args[3]))]
        else:
            return PcObject.restize_global_error(e)

    @staticmethod
    def save(*objects):
        if not objects:
            return None

        # CUMULATE ERRORS IN ONE SINGLE API ERRORS DURING ADD TIME
        api_errors = ApiErrors()
        for obj in objects:
            with db.session.no_autoflush:
                obj_api_errors = obj.errors()
            if obj_api_errors.errors.keys():
                api_errors.errors.update(obj_api_errors.errors)
            else:
                db.session.add(obj)

        # CHECK BEFORE COMMIT
        if api_errors.errors.keys():
            raise api_errors

        # COMMIT
        try:
            db.session.commit()
        except DataError as de:
            api_errors.addError(*PcObject.restize_data_error(de))
            raise api_errors
        except IntegrityError as ie:
            api_errors.addError(*PcObject.restize_integrity_error(ie))
            raise api_errors
        except InternalError as ie:
            for obj in objects:
                api_errors.addError(*obj.restize_internal_error(ie))
            raise api_errors
        except TypeError as te:
            api_errors.addError(*PcObject.restize_type_error(te))
            raise api_errors
        except ValueError as ve:
            api_errors.addError(*PcObject.restize_value_error(ve))
            raise api_errors

        if api_errors.errors.keys():
            raise api_errors

    @staticmethod
    def delete(model: Model):
        db.session.delete(model)
        db.session.commit()

    @staticmethod
    def _get_keys_to_populate(columns: Iterable[str], data: dict, skipped_keys: Iterable[str]) -> Set[str]:
        requested_columns_to_update = set(data.keys())
        forbidden_columns = set(['id', 'deleted'] + skipped_keys)
        allowed_columns_to_update = requested_columns_to_update - forbidden_columns
        keys_to_populate = set(columns).intersection(allowed_columns_to_update)
        return keys_to_populate

    def _try_to_set_attribute_with_deserialized_datetime(self, col, key, value):
        try:
            datetime_value = _deserialize_datetime(key, value)
            setattr(self, key, datetime_value)
        except TypeError:
            error = DateTimeCastError()
            error.addError(col.name, "Invalid value for %s (datetime): %r" % (key, value))
            raise error

    def _try_to_set_attribute_with_uuid(self, col, key, value):
        try:
            uuid_obj = uuid.UUID(value)
            setattr(self, key, value)
        except ValueError:
            error = UuidCastError()
            error.addError(col.name, "Invalid value for %s (uuid): %r" % (key, value))
            raise error

    def _try_to_set_attribute_with_decimal_value(self, col, key, value, expected_format):
        try:
            setattr(self, key, Decimal(value))
        except InvalidOperation:
            error = DecimalCastError()
            error.addError(col.name, "Invalid value for {} ({}): '{}'".format(key, expected_format, value))
            raise error

    def _check_not_soft_deleted(self):
        if self.is_soft_deleted():
            raise DeletedRecordException


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

def _is_human_id_column(column):
    key = column.key
    return (key == 'id' or key.endswith('Id')) and \
           (isinstance(column.type, BigInteger) or isinstance(column.type, Integer))

def _dehumanize_if_needed(column, value: Any) -> Any:
    if _is_human_id_column(column):
        return dehumanize(value)
    return value


def _format_into_ISO_8601(value):
    return value.isoformat() + "Z"


def _deserialize_datetime(key, value):
    if value is None:
        return None

    valid_patterns = ['%Y-%m-%dT%H:%M:%S.%fZ', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%SZ']
    datetime_value = None

    for pattern in valid_patterns:
        if match_format(value, pattern):
            datetime_value = datetime.strptime(value, pattern)

    if not datetime_value:
        raise TypeError('Invalid value for %s: %r' % (key, value), 'datetime', key)

    return datetime_value
