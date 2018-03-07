from collections import OrderedDict
from datetime import datetime
from decimal import Decimal, InvalidOperation
from enum import Enum
from flask import current_app as app, request
from pprint import pprint
from psycopg2.extras import DateTimeRange
from sqlalchemy.orm.collections import InstrumentedList
from utils.human_ids import dehumanize, humanize

db = app.db


class PcObject():
    id = db.Column(db.BigInteger,
                   primary_key=True,
                   autoincrement=True)

    def __init__(self, **options):
        if options and 'from_dict' in options and options['from_dict']:
            self.populateFromDict(options['from_dict'])

    def _asdict(self, **options):
        result = OrderedDict()
        for key in self.__mapper__.c.keys():
            value = getattr(self, key)
            if isinstance(value, Enum):
                result[key] = value.name
            elif isinstance(value, datetime):
                result[key] = value.isoformat()
            elif isinstance(value, DateTimeRange):
                result[key] = {'start': value.lower,
                               'end': value.upper}
            elif isinstance(value, list)\
                 and len(value)>0\
                 and isinstance(value[0], DateTimeRange):
                result[key] = list(map(lambda d: {'start': d.lower,
                                                  'end': d.upper},
                                       value))
            elif key == 'id' or key.endswith('Id'):
                result[key] = humanize(value)
            elif not key == 'thumb':  # FIXME: get rid of blobs properly
                result[key] = value
        if options and options['include_joins']:
            for join in options['include_joins']:
                if isinstance(join, dict):
                    key = join['key']
                    refine = join.get('refine')
                    resolve = join.get('resolve')
                    sub_joins = join.get('sub_joins')
                else:
                    key = join
                    refine = None
                    resolve = None
                    sub_joins = None
                if hasattr(self, key):
                    value = getattr(self, key)
                if not value is None:
                    if isinstance(value, InstrumentedList) or value.__class__.__name__=='AppenderBaseQuery':
                        if refine is None:
                            final_value = value
                        else:
                            final_value = refine(value, options.get('filters', {}))
                        result[key] = list(
                            map(
                                lambda attr: attr._asdict(
                                    include_joins=sub_joins
                                ),
                                final_value
                            )
                        )
                        if resolve != None:
                            result[key] = list(map(lambda v: resolve(v, options.get('filters', {})),
                                                   result[key]))
                    else:
                        result[key] = value._asdict(
                            include_joins=sub_joins
                        )
                        if resolve != None:
                            result[key] = resolve(result[key], options.get('filters', {}))

        return result

    def dump(self):
        pprint(vars(self))

    def errors(self):
        errors = app.model.ApiErrors()
        data = self.__class__.__table__.columns._data
        for key in data.keys():
            col = data[key]
            val = getattr(self, key)
            if not isinstance(col, db.Column):
                continue
            if not col.nullable\
               and not col.foreign_keys\
               and not col.primary_key\
               and col.default is None\
               and val is None:
                errors.addError(field=key, errtype='missing', error='is mandatory')
            if val is None:
                continue
            if (isinstance(col.type, db.String) or isinstance(col.type, db.CHAR))\
               and not isinstance(col.type, db.Enum)\
               and not isinstance(val, str):
                errors.addError(field=key, errtype='format', error='should be a string')
            if (isinstance(col.type, db.String) or isinstance(col.type, db.CHAR))\
               and isinstance(val, str)\
               and col.type.length\
               and len(val)>col.type.length:
                errors.addError(field=key,
                                errtype='length',
                                error='should be less than '
                                      + str(col.type.length)
                                      + ' characters long')
            if isinstance(col.type, db.Integer)\
               and not isinstance(val, int):
                errors.addError(field=key,
                                errtype='format',
                                error='should be an integer')
            if isinstance(col.type, db.Float)\
               and not isinstance(val, float):
                errors.addError(field=key,
                                errtype='format',
                                error='should be a float')
        return errors

    def abortIfErrors(self):
        apiErrors = self.errors()
        if apiErrors.errors:
            raise apiErrors

    def populateFromDict(self, dct):
        data = dct.copy()
        if data.__contains__('id'):
                del data['id']
        cols = self.__class__.__table__.columns._data
        for key in data.keys():
            if key=='deleted':
                continue
            if cols.__contains__(key):
                col = cols[key]
                if key.endswith('Id'):
                    value = dehumanize(data.get(key))
                else:
                    value = data.get(key)
                if isinstance(value, str) and isinstance(col.type, db.Integer):
                    try:
                        setattr(self, key, Decimal(value))
                    except InvalidOperation as io:
                        raise TypeError('Invalid value for %s: %r' % (key, value),
                                        'integer',
                                        key)
                elif isinstance(value, str) and (isinstance(col.type, db.Float) or isinstance(col.type, db.Numeric)):
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
        for obj in objects:
            if isinstance(obj, app.model.ProvidableMixin)\
                and request\
                and hasattr(request, 'provider'):
                obj.lastProvider = request.provider
            obj.abortIfErrors()
            db.session.add(obj)
        db.session.commit()

    def soft_delete(self):
        self.deleted = True
        db.session.add(self)

    def __repr__(self):
        return '<%s #%r>' % (self.__class__.__name__, self.id)

app.model.PcObject = PcObject
