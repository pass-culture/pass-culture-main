import logging

from alembic import context
from sqlalchemy import create_engine
from sqlalchemy import schema

from pcapi import settings
from pcapi.models import Base


logger = logging.getLogger(__name__)

target_metadata = Base.metadata


def include_object(
    object: schema.SchemaItem,  # pylint: disable=redefined-builtin
    name: str,
    type_: str,
    reflected: bool,
    compare_to: schema.SchemaItem | None,
) -> bool:
    # Don't generate DROP tables with autogenerate
    # https://alembic.sqlalchemy.org/en/latest/cookbook.html#don-t-generate-any-drop-table-directives-with-autogenerate
    if type_ == "table" and reflected and compare_to is None:
        table_name = object.name  # type: ignore[attr-defined]
        logger.warning(">>>>> Ignoring DROP TABLE for table '%s' <<<<<", table_name)
        return False
    return True


def run_migrations() -> None:
    db_options = []
    if settings.DB_MIGRATION_LOCK_TIMEOUT:
        db_options.append("-c lock_timeout=%i" % settings.DB_MIGRATION_LOCK_TIMEOUT)
    if settings.DB_MIGRATION_STATEMENT_TIMEOUT:
        db_options.append("-c statement_timeout=%i" % settings.DB_MIGRATION_STATEMENT_TIMEOUT)

    connectable = create_engine(settings.DATABASE_URL, connect_args={"options": " ".join(db_options)})

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_object=include_object,
            include_schemas=True,
            transaction_per_migration=True,
            compare_server_default=True,
        )
        with context.begin_transaction():
            context.run_migrations()
