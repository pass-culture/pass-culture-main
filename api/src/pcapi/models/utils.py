import typing

import sqlalchemy.orm as sa_orm
from werkzeug.exceptions import NotFound

from pcapi import models
from pcapi.models import db


T = typing.TypeVar("T", bound=models.Model)


def get_or_404_from_query(query: "sa_orm.Query[T]", obj_id: int | str) -> T:
    obj = query.filter_by(id=obj_id).one_or_none()
    if not obj:
        raise NotFound()
    return obj


def get_or_404(model: typing.Type[T], obj_id: int | str) -> T:
    return get_or_404_from_query(db.session.query(model), obj_id)


def first_or_404(query: "sa_orm.Query[T]") -> T:
    obj = query.first()
    if not obj:
        raise NotFound()
    return obj
