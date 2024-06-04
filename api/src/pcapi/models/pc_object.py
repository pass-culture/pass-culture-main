import logging
from pprint import pprint
import re
import typing

from flask_sqlalchemy import BaseQuery as FlaskSQLAlchemyBaseQuery
from sqlalchemy import BigInteger
import sqlalchemy.exc as sa_exc
import sqlalchemy.orm as sa_orm
from sqlalchemy.sql.schema import Column
from werkzeug.exceptions import NotFound

from pcapi.models import db


logger = logging.getLogger(__name__)


DUPLICATE_KEY_ERROR_CODE = "23505"
NOT_FOUND_KEY_ERROR_CODE = "23503"
OBLIGATORY_FIELD_ERROR_CODE = "23502"


class BaseQuery(FlaskSQLAlchemyBaseQuery):
    def get_or_404(self, obj_id: int) -> typing.Any:
        obj = self.filter_by(id=obj_id).one_or_none()
        if not obj:
            raise NotFound()
        return obj

    def get(self, pk: int) -> typing.Any:
        mapper = self._raw_columns[0]._annotations["parententity"]
        obj = db.session.get(mapper, pk)
        return obj


class DeletedRecordException(Exception):
    pass


class PcObject:
    query_class = BaseQuery

    id: sa_orm.Mapped[int] = Column(BigInteger, primary_key=True, autoincrement=True)

    def __init__(self, **kwargs: typing.Any) -> None:
        from_dict = kwargs.pop("from_dict", None)
        if from_dict:
            raise NotImplementedError()
        super().__init__(**kwargs)

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        return f"<{class_name} #{self.id or 'unsaved'}>"

    def dump(self) -> None:
        pprint(vars(self))

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
            return (type_error.args[2], "doit être une liste de nombre décimaux comme par exemple : [2.22, 3.22]")
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
                " doit être dans cette liste : " + ",".join(map(lambda x: '"' + x + '"', value_error.args[3])),
            )
        return PcObject.restize_global_error(value_error)
