import logging
import typing
from pprint import pprint

import sqlalchemy as sa
import sqlalchemy.orm as sa_orm


logger = logging.getLogger(__name__)


DUPLICATE_KEY_ERROR_CODE = "23505"
NOT_FOUND_KEY_ERROR_CODE = "23503"
OBLIGATORY_FIELD_ERROR_CODE = "23502"


class DeletedRecordException(Exception):
    pass


class PcObject:
    id: sa_orm.Mapped[int] = sa_orm.mapped_column(sa.BigInteger, primary_key=True, autoincrement=True)

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
