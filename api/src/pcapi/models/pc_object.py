from datetime import datetime
from decimal import Decimal
from decimal import InvalidOperation
import logging
from pprint import pprint
import re
from typing import Any
from typing import Iterable
import uuid

from sqlalchemy import BigInteger
from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import Integer
from sqlalchemy import Numeric
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql.schema import Column

from pcapi.models.api_errors import DateTimeCastError
from pcapi.models.api_errors import DecimalCastError
from pcapi.models.api_errors import UuidCastError
from pcapi.models.soft_deletable_mixin import SoftDeletableMixin
from pcapi.utils.human_ids import dehumanize
from pcapi.utils.human_ids import humanize


logger = logging.getLogger(__name__)


DUPLICATE_KEY_ERROR_CODE = "23505"
NOT_FOUND_KEY_ERROR_CODE = "23503"
OBLIGATORY_FIELD_ERROR_CODE = "23502"


class DeletedRecordException(Exception):
    pass


class PcObject:
    id = Column(BigInteger, primary_key=True, autoincrement=True)

    def __init__(self, **kwargs):  # type: ignore [no-untyped-def]
        from_dict = kwargs.pop("from_dict", None)
        if from_dict:
            self.populate_from_dict(from_dict)
        super().__init__(**kwargs)

    def __repr__(self):  # type: ignore [no-untyped-def]
        if self.id is None:
            object_id = "unsaved"
        else:
            object_id = f"{self.id}/{humanize(self.id)}"
        return "<%s #%s>" % (self.__class__.__name__, object_id)

    def dump(self):  # type: ignore [no-untyped-def]
        pprint(vars(self))

    def populate_from_dict(self, data: dict, skipped_keys: Iterable[str] = ()):  # type: ignore [no-untyped-def]
        self._check_not_soft_deleted()
        columns = self.__mapper__.column_attrs  # type: ignore [attr-defined]
        keys_to_populate = self._get_keys_to_populate(columns.keys(), data, skipped_keys)

        for key in keys_to_populate:
            column = columns[key]
            value = _dehumanize_if_needed(column, data.get(key))
            if isinstance(value, str):
                if isinstance(column.expression.type, Integer):
                    self._try_to_set_attribute_with_decimal_value(column, key, value, "integer")
                elif isinstance(column.expression.type, (Float, Numeric)):
                    self._try_to_set_attribute_with_decimal_value(column, key, value, "float")
                elif isinstance(column.expression.type, String):
                    setattr(self, key, value.strip() if value else value)
                elif isinstance(column.expression.type, DateTime):
                    self._try_to_set_attribute_with_deserialized_datetime(column, key, value)
                elif isinstance(column.expression.type, UUID):
                    self._try_to_set_attribute_with_uuid(column, key, value)
            elif not isinstance(value, datetime) and isinstance(column.expression.type, DateTime):
                self._try_to_set_attribute_with_deserialized_datetime(column, key, value)
            else:
                setattr(self, key, value)

    def is_soft_deleted(self):  # type: ignore [no-untyped-def]
        return issubclass(type(self), SoftDeletableMixin) and self.isSoftDeleted

    @staticmethod
    def restize_global_error(global_error):  # type: ignore [no-untyped-def]
        logger.exception("UNHANDLED ERROR : %s", global_error)
        return [
            "global",
            "Une erreur technique s'est produite. Elle a été notée, et nous allons investiguer au plus vite.",
        ]

    @staticmethod
    def restize_data_error(data_error):  # type: ignore [no-untyped-def]
        if (
            data_error.args
            and len(data_error.args) > 0
            and data_error.args[0].startswith("(psycopg2.DataError) value too long for type")
        ):
            max_length = re.search(
                r"\(psycopg2.DataError\) value too long for type (.*?) varying\((.*?)\)",
                data_error.args[0],
                re.IGNORECASE,
            ).group(2)
            return ["global", "La valeur d'une entrée est trop longue (max " + max_length + ")"]
        return PcObject.restize_global_error(data_error)

    @staticmethod
    def restize_integrity_error(integrity_error):  # type: ignore [no-untyped-def]
        if (
            hasattr(integrity_error, "orig")
            and hasattr(integrity_error.orig, "pgcode")
            and integrity_error.orig.pgcode == DUPLICATE_KEY_ERROR_CODE
        ):
            field = re.search(r"Key \((.*?)\)=", str(integrity_error._message), re.IGNORECASE).group(1)
            if "," in field:
                field = "global"
            return [field, "Une entrée avec cet identifiant existe déjà dans notre base de données"]
        if (
            hasattr(integrity_error, "orig")
            and hasattr(integrity_error.orig, "pgcode")
            and integrity_error.orig.pgcode == NOT_FOUND_KEY_ERROR_CODE
        ):
            field = re.search(r"Key \((.*?)\)=", str(integrity_error._message), re.IGNORECASE).group(1)
            return [field, "Aucun objet ne correspond à cet identifiant dans notre base de données"]
        if (
            hasattr(integrity_error, "orig")
            and hasattr(integrity_error.orig, "pgcode")
            and integrity_error.orig.pgcode == OBLIGATORY_FIELD_ERROR_CODE
        ):
            field = re.search('column "(.*?)"', integrity_error.orig.pgerror, re.IGNORECASE).group(1)
            return [field, "Ce champ est obligatoire"]
        return PcObject.restize_global_error(integrity_error)

    @staticmethod
    def restize_internal_error(internal_error):  # type: ignore [no-untyped-def]
        return PcObject.restize_global_error(internal_error)

    @staticmethod
    def restize_type_error(type_error):  # type: ignore [no-untyped-def]
        if type_error.args and len(type_error.args) > 1 and type_error.args[1] == "geography":
            return [type_error.args[2], "doit etre une liste de nombre décimaux comme par exemple : [2.22, 3.22]"]
        if type_error.args and len(type_error.args) > 1 and type_error.args[1] and type_error.args[1] == "decimal":
            return [type_error.args[2], "doit être un nombre décimal"]
        if type_error.args and len(type_error.args) > 1 and type_error.args[1] and type_error.args[1] == "integer":
            return [type_error.args[2], "doit être un entier"]
        return PcObject.restize_global_error(type_error)

    @staticmethod
    def restize_value_error(value_error):  # type: ignore [no-untyped-def]
        if len(value_error.args) > 1 and value_error.args[1] == "enum":
            return [
                value_error.args[2],
                " doit etre dans cette liste : " + ",".join(map(lambda x: '"' + x + '"', value_error.args[3])),
            ]
        return PcObject.restize_global_error(value_error)

    @staticmethod
    def _get_keys_to_populate(columns: Iterable[str], data: dict, skipped_keys: Iterable[str]) -> set[str]:
        requested_columns_to_update = set(data.keys())
        forbidden_columns = {"id", "deleted"} | set(skipped_keys)
        allowed_columns_to_update = requested_columns_to_update - forbidden_columns
        keys_to_populate = set(columns).intersection(allowed_columns_to_update)
        return keys_to_populate

    def _try_to_set_attribute_with_deserialized_datetime(self, col, key, value):  # type: ignore [no-untyped-def]
        try:
            datetime_value = _deserialize_datetime(value)
            setattr(self, key, datetime_value)
        except TypeError:
            error = DateTimeCastError()
            error.add_error(col.expression.name, "Invalid value for %s (datetime): %r" % (key, value))
            raise error

    def _try_to_set_attribute_with_uuid(self, col, key, value):  # type: ignore [no-untyped-def]
        try:
            uuid.UUID(value)
            setattr(self, key, value)
        except ValueError:
            error = UuidCastError()
            error.add_error(col.expression.name, "Invalid value for %s (uuid): %r" % (key, value))
            raise error

    def _try_to_set_attribute_with_decimal_value(self, col, key, value, expected_format):  # type: ignore [no-untyped-def]
        try:
            setattr(self, key, Decimal(value))
        except InvalidOperation:
            error = DecimalCastError()
            error.add_error(col.expression.name, "Invalid value for {} ({}): '{}'".format(key, expected_format, value))
            raise error

    def _check_not_soft_deleted(self):  # type: ignore [no-untyped-def]
        if self.is_soft_deleted():
            raise DeletedRecordException


def _dehumanize_if_needed(column, value: Any) -> Any:  # type: ignore [no-untyped-def]
    if _is_human_id_column(column) and not isinstance(value, int):
        return dehumanize(value)
    return value


def _deserialize_datetime(value):  # type: ignore [no-untyped-def]
    if value is None:
        return None

    valid_formats = ["%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%SZ"]
    for format_ in valid_formats:
        try:
            return datetime.strptime(value, format_)
        except ValueError:
            pass

    raise TypeError()


def _is_human_id_column(column: Column) -> bool:
    if column is None:
        return None
    column_name = column.key
    is_column_primary_key_or_foreign_key = column_name == "id" or column_name.endswith("Id")  # type: ignore [union-attr]
    is_column_a_number = isinstance(column.expression.type, (Integer, BigInteger))
    return is_column_primary_key_or_foreign_key and is_column_a_number
