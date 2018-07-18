""" pc_object """
from collections import OrderedDict
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pprint import pprint
from psycopg2.extras import DateTimeRange
from sqlalchemy import CHAR,\
                       BigInteger,\
                       Column,\
                       Enum,\
                       Float,\
                       Integer,\
                       Numeric,\
                       String
from sqlalchemy.orm.collections import InstrumentedList

from models.api_errors import ApiErrors
from models.db import db
from utils.human_ids import dehumanize, humanize


def serialize(value, **options):
    if isinstance(value, Enum):
        return value.name
    elif isinstance(value, datetime):
        return value.isoformat()+"Z"
    elif isinstance(value, DateTimeRange):
        return {
            'start': value.lower,
            'end': value.upper
        }
    elif isinstance(value, list)\
            and len(value) > 0\
            and isinstance(value[0], DateTimeRange):
        return list(map(lambda d: {'start': d.lower,
                                   'end': d.upper},
                        value))
    else:
        return value


class PcObject():
    id = Column(BigInteger,
                primary_key=True,
                autoincrement=True)

    def __init__(self, **options):
        if options and 'from_dict' in options and options['from_dict']:
            self.populateFromDict(options['from_dict'])

    def _asdict(self, **options):
        result = OrderedDict()
        for key in self.__mapper__.c.keys():
            if options\
               and 'include' in options\
               and options.get('include')\
               and "-"+key in options['include']:
                continue
            value = getattr(self, key)
            if options and options.get('cut'):
                if isinstance(value, str):
                    if len(value) > options['cut']:
                        value = value[:options['cut']] + '...'
            if key == 'id' or key.endswith('Id'):
                result[key] = humanize(value)
                result['dehumanized' + key[0].capitalize() + key[1:]] = value
            elif key == 'validationToken':
                continue
            elif key == 'firstThumbDominantColor' and value:
                result[key] = list(value)
            else:
                result[key] = serialize(value, **options)
        # add the model name
        result['modelName'] = self.__class__.__name__
        if options\
           and 'include' in options\
           and options['include']:
            for join in options['include']:
                if isinstance(join, str) and\
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
                    if isinstance(value, InstrumentedList)\
                       or value.__class__.__name__ == 'AppenderBaseQuery'\
                       or isinstance(value, list):
                        if refine is None:
                            final_value = value
                        else:
                            final_value = refine(value, options.get('filters', {}))
                        result[key] = list(
                            map(
                                lambda attr: attr._asdict(
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
                        result[key] = value._asdict(
                            include=sub_joins,
                            cut=options and options.get('cut'),
                        )
                        if resolve != None:
                            result[key] = resolve(result[key], options.get('filters', {}))
                    else:
                        result[key] = serialize(value)

        if options and\
           'resolve' in options and\
           options['resolve']:
            return options['resolve'](result, options.get('filters', {}))
        else:
            return result

    def dump(self):
        pprint(vars(self))

    def errors(self):
        errors = ApiErrors()
        data = self.__class__.__table__.columns._data
        for key in data.keys():
            col = data[key]
            val = getattr(self, key)
            if not isinstance(col, Column):
                continue
            if not col.nullable\
               and not col.foreign_keys\
               and not col.primary_key\
               and col.default is None\
               and val is None:
                errors.addError(key, 'Cette information est obligatoire')
            if val is None:
                continue
            if (isinstance(col.type, String) or isinstance(col.type, CHAR))\
               and not isinstance(col.type, Enum)\
               and not isinstance(val, str):
                errors.addError(key, 'doit être une chaîne de caractères')
            if (isinstance(col.type, String) or isinstance(col.type, CHAR))\
               and isinstance(val, str)\
               and col.type.length\
               and len(val)>col.type.length:
                errors.addError(key,
                                'Vous devez saisir moins de '
                                      + str(col.type.length)
                                      + ' caractères')
            if isinstance(col.type, Integer)\
               and not isinstance(val, int):
                errors.addError(key, 'doit être un entier')
            if isinstance(col.type, Float)\
               and not isinstance(val, float):
                errors.addError(key, 'doit être un nombre')
        return errors

    def abortIfErrors(self):
        apiErrors = self.errors()
        if apiErrors.errors:
            print(apiErrors.errors)
            raise apiErrors

    def populateFromDict(self, dct, skipped_keys=[]):
        data = dct.copy()
        if data.__contains__('id'):
                del data['id']
        cols = self.__class__.__table__.columns._data
        for key in data.keys():
            if (key=='deleted') or (key in skipped_keys):
                continue
            if cols.__contains__(key):
                col = cols[key]
                if key.endswith('Id'):
                    value = dehumanize(data.get(key))
                else:
                    value = data.get(key)
                if isinstance(value, str) and isinstance(col.type, Integer):
                    try:
                        setattr(self, key, Decimal(value))
                    except InvalidOperation as io:
                        raise TypeError('Invalid value for %s: %r' % (key, value),
                                        'integer',
                                        key)
                elif isinstance(value, str) and (isinstance(col.type, Float) or isinstance(col.type,Numeric)):
                    try:
                        setattr(self, key, Decimal(value))
                    except InvalidOperation as io:
                        raise TypeError('Invalid value for %s: %r' % (key, value),
                                        'decimal',
                                        key)
                else:
                    setattr(self, key, value)

    @staticmethod
    def check_and_save(*objects):
        if len(objects)==0:
            raise ValueError('Objects to save need to be passed as arguments'
                             + ' to check_and_save')
        for obj in objects:
            obj.abortIfErrors()
            db.session.add(obj)
        db.session.commit()

    def soft_delete(self):
        self.deleted = True
        db.session.add(self)

    def __repr__(self):
        id = "unsaved"\
               if self.id is None\
               else str(self.id) + "/" + humanize(self.id)
        return '<%s #%s>' % (self.__class__.__name__,
                             id)
