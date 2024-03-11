import typing


if typing.TYPE_CHECKING:
    hybrid_property = property
else:
    from sqlalchemy.ext.hybrid import hybrid_property


# Lifted from https://github.com/sqlalchemy/sqlalchemy2-stubs/issues/171
#
# This `hybrid_property` can be used to work around some (but not all)
# errors raised by mypy when decorated by the SQLAlchemy's function of
# the same name.
#
# It must only be used like this:
#
#     if typing.TYPE_CHECKING:
#         from pcapi.utils.typing import hybrid_property
#     else:
#         from sqlalchemy.ext.hybrid import hybrid_property
#
# FIXME: DEBUG ONLY : this looks nice but does not bring anything more
# than using `property`. We still have the same errors (and, in fact
# mypy 0.991 reports errors on this class).
#
# import typing
#
# import sqlalchemy as sqla
#
# _T_FOR_HYBRID_PROPERTY = typing.TypeVar("_T_FOR_HYBRID_PROPERTY")


# class hybrid_property(typing.Generic[_T_FOR_HYBRID_PROPERTY]):
#     def __init__(
#         self,
#         fget: typing.Callable[[typing.Any], _T_FOR_HYBRID_PROPERTY],
#         expr: typing.Callable[[typing.Any], sqla.sql.ColumnElement[_T_FOR_HYBRID_PROPERTY]],
#     ):
#         self.fget = fget
#         self.expr = expr

#     @typing.overload
#     def __get__(
#         self,
#         instance: None,
#         owner: typing.Type[typing.Any] | None,
#     ) -> "sqla.sql.ColumnElement[_T_FOR_HYBRID_PROPERTY]":
#         ...

#     @typing.overload
#     def __get__(
#         self,
#         instance: object,
#         owner: typing.Type[typing.Any] or None,
#     ) -> _T_FOR_HYBRID_PROPERTY:
#         ...

#     def __get__(
#         self,
#         instance: object | None,
#         owner: typing.Type[typing.Any] | None = None,
#     ) -> typing.Any:
#         if instance is None:
#             return self.expr(owner)
#         else:
#             return self.fget(instance)

#     def expression(
#         self,
#         expr: "typing.Callable[[typing.Any], sqla.sql.ColumnElement[_T_FOR_HYBRID_PROPERTY]]",
#     ) -> bool:  #  "hybrid_property[_T_FOR_HYBRID_PROPERTY]"
#         return hybrid_property(self.fget, expr)
