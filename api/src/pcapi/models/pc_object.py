from datetime import datetime
from decimal import Decimal
from decimal import InvalidOperation
import logging
from pprint import pprint
import re
import typing
import uuid

from sqlalchemy import BigInteger
from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import Integer
from sqlalchemy import Numeric
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID
import sqlalchemy.exc as sa_exc
import sqlalchemy.orm as sa_orm
from sqlalchemy.sql.schema import Column

from pcapi.models.api_errors import DateTimeCastError
from pcapi.models.api_errors import DecimalCastError
from pcapi.models.api_errors import UuidCastError
from pcapi.utils.human_ids import dehumanize
from pcapi.utils.human_ids import humanize


logger = logging.getLogger(__name__)


DUPLICATE_KEY_ERROR_CODE = "23505"
NOT_FOUND_KEY_ERROR_CODE = "23503"
OBLIGATORY_FIELD_ERROR_CODE = "23502"


class DeletedRecordException(Exception):
    pass


class PcObject:
    id: sa_orm.Mapped[int] = Column(BigInteger, primary_key=True, autoincrement=True)  # type: ignore [assignment]

    def __init__(self, **kwargs: typing.Any) -> None:
        from_dict = kwargs.pop("from_dict", None)
        if from_dict:
            self.populate_from_dict(from_dict)
        super().__init__(**kwargs)

    def __repr__(self) -> str:
        if self.id is None:
            object_id = "unsaved"
        else:
            object_id = f"{self.id}/{humanize(self.id)}"
        return "<%s #%s>" % (self.__class__.__name__, object_id)

    def dump(self) -> None:
        pprint(vars(self))

    def populate_from_dict(self, data: dict, skipped_keys: typing.Iterable[str] = ()) -> None:
        self._check_not_soft_deleted()
        mapper: sa_orm.Mapper = self.__mapper__  # type: ignore [attr-defined]
        columns = mapper.all_orm_descriptors
        keys_to_populate = self._get_keys_to_populate(columns.keys(), data, skipped_keys)

        for key in keys_to_populate:
            column = mapper.column_attrs.get(key)
            if not column:  # key is not a column, so probably an hybrid property
                setattr(self, key, data.get(key))
                continue

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

    def is_soft_deleted(self) -> bool:
        return getattr(self, "isSoftDeleted", False)

    @staticmethod
    def restize_global_error(global_error: Exception) -> tuple[str, str]:
        logger.exception("UNHANDLED ERROR : %s", global_error)
        return (
            "global",
            "Une erreur technique s'est produite. Elle a été notée, et nous allons investiguer au plus vite.",
        )

    @staticmethod
    def restize_data_error(data_error: sa_exc.DataError) -> tuple[str, str]:
        if data_error.args and len(data_error.args) > 0:
            if match := re.search(
                r"\(psycopg2.DataError\) value too long for type (.*?) varying\((.*?)\)",
                data_error.args[0],
                re.IGNORECASE,
            ):
                max_length = match.group(2)
                return ("global", "La valeur d'une entrée est trop longue (max " + max_length + ")")
        return PcObject.restize_global_error(data_error)

    @staticmethod
    def restize_integrity_error(integrity_error: sa_exc.IntegrityError) -> tuple[str, str]:
        message = integrity_error.args[0]
        if not hasattr(getattr(integrity_error, "orig"), "pgcode"):
            return PcObject.restize_global_error(integrity_error)
        if integrity_error.orig.pgcode == DUPLICATE_KEY_ERROR_CODE:
            if m := re.search(r"Key \((.*?)\)=", message, re.IGNORECASE):
                field = m.group(1)
                if "," in field:
                    field = "global"
                return (field, "Une entrée avec cet identifiant existe déjà dans notre base de données")
        elif integrity_error.orig.pgcode == NOT_FOUND_KEY_ERROR_CODE:
            if m := re.search(r"Key \((.*?)\)=", message, re.IGNORECASE):
                field = m.group(1)
                return (field, "Aucun objet ne correspond à cet identifiant dans notre base de données")
        if integrity_error.orig.pgcode == OBLIGATORY_FIELD_ERROR_CODE:
            if m := re.search('column "(.*?)"', integrity_error.orig.pgerror, re.IGNORECASE):
                field = m.group(1)
                return (field, "Ce champ est obligatoire")
        return PcObject.restize_global_error(integrity_error)

    @staticmethod
    def restize_internal_error(internal_error: sa_exc.InternalError) -> tuple[str, str]:
        return PcObject.restize_global_error(internal_error)

    @staticmethod
    def restize_type_error(type_error: TypeError) -> tuple[str, str]:
        if type_error.args and len(type_error.args) > 1 and type_error.args[1] == "geography":
            return (type_error.args[2], "doit etre une liste de nombre décimaux comme par exemple : [2.22, 3.22]")
        if type_error.args and len(type_error.args) > 1 and type_error.args[1] and type_error.args[1] == "decimal":
            return (type_error.args[2], "doit être un nombre décimal")
        if type_error.args and len(type_error.args) > 1 and type_error.args[1] and type_error.args[1] == "integer":
            return (type_error.args[2], "doit être un entier")
        return PcObject.restize_global_error(type_error)

    @staticmethod
    def restize_value_error(value_error: ValueError) -> tuple[str, str]:
        if len(value_error.args) > 1 and value_error.args[1] == "enum":
            return (
                value_error.args[2],
                " doit etre dans cette liste : " + ",".join(map(lambda x: '"' + x + '"', value_error.args[3])),
            )
        return PcObject.restize_global_error(value_error)

    @staticmethod
    def _get_keys_to_populate(
        columns: typing.Iterable[str],
        data: dict,
        skipped_keys: typing.Iterable[str],
    ) -> set[str]:
        requested_columns_to_update = set(data.keys())
        forbidden_columns = {"id", "deleted"} | set(skipped_keys)
        allowed_columns_to_update = requested_columns_to_update - forbidden_columns
        keys_to_populate = set(columns).intersection(allowed_columns_to_update)
        return keys_to_populate

    def _try_to_set_attribute_with_deserialized_datetime(
        self,
        col: sa_orm.ColumnProperty,
        key: str,
        value: typing.Any,
    ) -> None:
        try:
            datetime_value = _deserialize_datetime(value)
            setattr(self, key, datetime_value)
        except TypeError:
            error = DateTimeCastError()
            error.add_error(col.expression.name, "Invalid value for %s (datetime): %r" % (key, value))
            raise error

    def _try_to_set_attribute_with_uuid(
        self,
        col: sa_orm.ColumnProperty,
        key: str,
        value: typing.Any,
    ) -> None:
        try:
            uuid.UUID(value)
            setattr(self, key, value)
        except ValueError:
            error = UuidCastError()
            error.add_error(col.expression.name, "Invalid value for %s (uuid): %r" % (key, value))
            raise error

    def _try_to_set_attribute_with_decimal_value(
        self,
        col: sa_orm.ColumnProperty,
        key: str,
        value: typing.Any,
        expected_format: str,
    ) -> None:
        try:
            setattr(self, key, Decimal(value))
        except InvalidOperation:
            error = DecimalCastError()
            error.add_error(col.expression.name, "Invalid value for {} ({}): '{}'".format(key, expected_format, value))
            raise error

    def _check_not_soft_deleted(self) -> None:
        if self.is_soft_deleted():
            raise DeletedRecordException


def _dehumanize_if_needed(column: sa_orm.ColumnProperty, value: typing.Any) -> typing.Any:
    if _is_human_id_column(column) and not isinstance(value, int):
        return dehumanize(value)
    return value


def _deserialize_datetime(value: str | None) -> datetime | None:
    if value is None:
        return None

    valid_formats = ["%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%SZ"]
    for format_ in valid_formats:
        try:
            return datetime.strptime(value, format_)
        except ValueError:
            pass

    raise TypeError()


def _is_human_id_column(column: sa_orm.ColumnProperty) -> bool:
    if column is None:
        return None
    column_name = column.key
    is_column_primary_key_or_foreign_key = column_name == "id" or column_name.endswith("Id")
    is_column_a_number = isinstance(column.expression.type, (Integer, BigInteger))
    return is_column_primary_key_or_foreign_key and is_column_a_number
