"""Filter soft-deleted venues out of ORM SELECT statements, without paying the cost on every query.

`SoftDeleteQueryRewriter` calls `Select.get_final_froms()`, which runs the whole ORM
compilation each time and bypasses SQLAlchemy's compiled cache. Most statements never
involve the `venue` table: their structure is remembered so that later executions skip
the rewrite and return the statement unchanged.
"""

import typing

import sqlalchemy as sa
import sqlalchemy.util as sa_util
from sqlalchemy_easy_softdelete.handler.rewriter import EnabledTable
from sqlalchemy_easy_softdelete.handler.rewriter import SoftDeleteQueryRewriter


DISABLE_SOFT_DELETE_OPTION_NAME = "include_deleted"

# Structures (SQLAlchemy cache keys, without bound values) for which a full rewrite
# added no filter. Bounded like SQLAlchemy's own compiled cache.
_statements_without_filter: sa_util.LRUCache = sa_util.LRUCache(1000)

StatementT = typing.TypeVar("StatementT")


class _TrackingRewriter(SoftDeleteQueryRewriter):
    """Record whether a rewrite added a filter or was disabled on one of the selects."""

    def __init__(self) -> None:
        super().__init__(
            deleted_field_name="isSoftDeleted",
            disable_soft_delete_option_name=DISABLE_SOFT_DELETE_OPTION_NAME,
            enabled_tables=[EnabledTable("venue", None)],
        )
        self.added_filter = False
        self.disabled_by_option = False

    def rewrite_select(self, stmt: sa.Select) -> sa.Select:
        if stmt.get_execution_options().get(self.disable_soft_delete_option_name):
            self.disabled_by_option = True
        return super().rewrite_select(stmt)

    def rewrite_from_table(self, stmt: sa.Select, table: sa.Table) -> sa.Select:
        rewritten = super().rewrite_from_table(stmt, table)
        if rewritten is not stmt:
            self.added_filter = True
        return rewritten


def rewrite_statement(statement: StatementT) -> StatementT:
    """Return `statement` with a `NOT isSoftDeleted` filter on every `venue` table it selects from.

    Skipping is only safe for a structure whose full rewrite added no filter and was
    not disabled by `include_deleted` anywhere: such a structure has no `venue` table
    to filter. Execution options are not part of SQLAlchemy cache keys, so a structure
    rewritten with `include_deleted` must not be remembered.
    """
    cache_key = statement._generate_cache_key()  # type: ignore[attr-defined]
    structure = cache_key.key if cache_key is not None else None
    if structure is not None and _statements_without_filter.get(structure):
        return statement

    rewriter = _TrackingRewriter()
    rewritten = rewriter.rewrite_statement(statement)
    # The rewriter may modify nested selects in place: drop the cache key memoized
    # above so that SQLAlchemy computes it again from the rewritten statement.
    statement._reset_memoizations()  # type: ignore[attr-defined]

    if structure is not None and not rewriter.added_filter and not rewriter.disabled_by_option:
        _statements_without_filter[structure] = True
    return typing.cast(StatementT, rewritten)
