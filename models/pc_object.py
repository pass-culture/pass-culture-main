""" pc_object """
from collections import OrderedDict
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pprint import pprint
import re
import traceback
from psycopg2.extras import DateTimeRange

from sqlalchemy import CHAR,\
                       BigInteger,\
                       Column,\
                       Enum,\
                       Float,\
                       Integer,\
                       Numeric,\
                       String
from sqlalchemy.exc import DataError, IntegrityError
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
        api_errors = ApiErrors()
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
                api_errors.addError(key, 'Cette information est obligatoire')
            if val is None:
                continue
            if (isinstance(col.type, String) or isinstance(col.type, CHAR))\
               and not isinstance(col.type, Enum)\
               and not isinstance(val, str):
                api_errors.addError(key, 'doit être une chaîne de caractères')
            if (isinstance(col.type, String) or isinstance(col.type, CHAR))\
               and isinstance(val, str)\
               and col.type.length\
               and len(val)>col.type.length:
                api_errors.addError(key,
                                'Vous devez saisir moins de '
                                      + str(col.type.length)
                                      + ' caractères')
            if isinstance(col.type, Integer)\
               and not isinstance(val, int):
                api_errors.addError(key, 'doit être un entier')
            if isinstance(col.type, Float)\
               and not isinstance(val, float):
                api_errors.addError(key, 'doit être un nombre')
        return api_errors

    @staticmethod
    def restize_global_error(e):
        print("UNHANDLED ERROR : ")
        traceback.print_exc()
        return ["global", "Une erreur technique s'est produite. Elle a été notée, et nous allons investiguer au plus vite."]

    @staticmethod
    def restize_data_error(e):
        if e.args and len(e.args) > 0 and e.args[0].startswith('(psycopg2.DataError) value too long for type'):
            max_length = re.search('\(psycopg2.DataError\) value too long for type (.*?) varying\((.*?)\)', e.args[0], re.IGNORECASE).group(2)
            return ['global', "La valeur d'une entrée est trop longue (max " + max_length + ")"]
        else:
            return PcObject.restize_global_error(e)

    @staticmethod
    def restize_integrity_error(e):
        if hasattr(e, 'orig') and hasattr(e.orig, 'pgcode') and e.orig.pgcode == '23505':
            field = re.search('Key \((.*?)\)=', str(e._message), re.IGNORECASE).group(1)
            return [field, 'Une entrée avec cet identifiant existe déjà dans notre base de données']
        elif hasattr(e, 'orig') and hasattr(e.orig, 'pgcode') and e.orig.pgcode == '23503':
            field = re.search('Key \((.*?)\)=', str(e._message), re.IGNORECASE).group(1)
            return [field, 'Aucun objet ne correspond à cet identifiant dans notre base de données']
        elif hasattr(e, 'orig') and hasattr(e.orig, 'pgcode') and e.orig.pgcode == '23502':
            field = re.search('column "(.*?)"', e.orig.pgerror, re.IGNORECASE).group(1)
            return [field, 'Ce champ est obligatoire']
        else:
            return PcObject.restize_global_error(e)

    @staticmethod
    def restize_type_error(e):
        if e.args and len(e.args)>1 and e.args[1] == 'geography':
            return [e.args[2], 'doit etre une liste de nombre décimaux comme par exemple : [2.22, 3.22]']
        elif e.args and len(e.args)>1 and e.args[1] and e.args[1]=='decimal':
            return [e.args[2], 'doit être un nombre décimal']
        elif e.args and len(e.args)>1 and e.args[1] and e.args[1]=='integer':
            return [e.args[2], 'doit être un entier']
        else:
            return PcObject.restize_global_error(e)

    @staticmethod
    def restize_value_error(e):
        if len(e.args)>1 and e.args[1] == 'enum':
            return [e.args[2], ' doit etre dans cette liste : '+",".join(map(lambda x : '"'+x+'"', e.args[3]))]
        else:
            return PcObject.restize_global_error(e)

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
    def check_and_save(*objects, **kwargs):
        if not objects:
            raise ValueError('Objects to save need to be passed as arguments'
                             + ' to check_and_save')
        # CUMULATE ERRORS IN ONE SINGLE API ERRORS DURING ADD TIME
        api_errors = ApiErrors()
        for obj in objects:
            obj_api_errors = obj.errors()
            api_errors.errors.update(obj_api_errors.errors)
            if not api_errors.errors.keys():
                db.session.add(obj)

        # CHECK BEFORE COMMIT
        if api_errors.errors.keys():
            raise api_errors

        # COMMIT
        try:
            db.session.commit()
        except DataError as de:
            if kwargs.get('restize_data_error'):
                error = kwargs.get('restize_data_error')(de)
                if error:
                    api_errors.addError(*error)
            api_errors.addError(*PcObject.restize_data_error(de))
            raise api_errors
        except IntegrityError as ie:
            if kwargs.get('restize_integrity_error'):
                error = kwargs.get('restize_integrity_error')(ie)
                if error:
                    api_errors.addError(*error)
            api_errors.addError(*PcObject.restize_integrity_error(ie))
            raise api_errors
        except TypeError as te:
            if kwargs.get('restize_type_error'):
                error = kwargs.get('restize_type_error')(te)
                if error:
                    api_errors.addError(*error)
            api_errors.addError(*PcObject.restize_type_error(te))
            raise api_errors
        except ValueError as ve:
            if kwargs.get('restize_value_error'):
                error = kwargs.get('restize_value_error')(ve)
                if error:
                    api_errors.addError(*error)
            api_errors.addError(*PcObject.restize_value_error(ve))
            raise api_errors
        if api_errors.errors.keys():
            raise api_errors

    @staticmethod
    def delete(model):
        db.session.delete(model)
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
