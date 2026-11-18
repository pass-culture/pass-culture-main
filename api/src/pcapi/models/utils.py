import os
import typing

import sqlalchemy as sa
import sqlalchemy.orm as sa_orm

from pcapi import models
from pcapi.models import db
from pcapi.models.api_errors import resource_not_found_error


T = typing.TypeVar("T", bound=models.Model)


def get_or_404_from_query(query: "sa_orm.Query[T]", obj_id: int | str) -> T:
    obj = query.filter_by(id=obj_id).one_or_none()
    if not obj:
        raise resource_not_found_error()
    return obj


def get_or_404(model: type[T], obj_id: int | str) -> T:
    return get_or_404_from_query(db.session.query(model), obj_id)


def first_or_404(query: "sa_orm.Query[T]") -> T:
    obj = query.first()
    if not obj:
        raise resource_not_found_error()
    return obj


############## Hooks SqlAlchemy ##############


# Invalidates connections that are being shared accross process boundaries
# see https://docs.sqlalchemy.org/en/13/core/pooling.html#using-connection-pools-with-multiprocessing-or-os-fork
def connect_hook(dbapi_connection: typing.Any, connection_record: typing.Any) -> None:
    connection_record.info["pid"] = os.getpid()


def checkout_hook(dbapi_connection: typing.Any, connection_record: typing.Any, connection_proxy: typing.Any) -> None:
    pid = os.getpid()
    if connection_record.info["pid"] != pid:
        connection_record.connection = connection_proxy.connection = None
        raise sa.exc.DisconnectionError(
            f"Connection record belongs to pid {connection_record.info['pid']}, attempting to check out in pid {pid}"
        )


def soft_delete_execute_hook(state: sa_orm.ORMExecuteState) -> None:
    import sqlalchemy_easy_softdelete.handler.rewriter as softdelete_rewriter

    # TODO: check with UPDATE and SELECT in subquery. Does it still work ?
    if not state.is_select:
        return

    # Rewrite the statement
    global_rewriter = softdelete_rewriter.SoftDeleteQueryRewriter(
        deleted_field_name="isSoftDeleted",
        disable_soft_delete_option_name="include_deleted",
        enabled_tables=[softdelete_rewriter.EnabledTable("venue", None)],
    )
    adapted = global_rewriter.rewrite_statement(state.statement)

    # Replace the statement
    state.statement = adapted
