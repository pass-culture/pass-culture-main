from alembic import context
from sqlalchemy import create_engine

from pcapi import settings
from pcapi.models.db import db


target_metadata = db.metadata


def include_object(object, name, type_, reflected, compare_to) -> bool:  # pylint: disable=redefined-builtin
    # Don't generate DROP tables with autogenerate
    # https://alembic.sqlalchemy.org/en/latest/cookbook.html#don-t-generate-any-drop-table-directives-with-autogenerate
    if type_ == "table" and reflected and compare_to is None:
        return False
    if name in ("transaction", "activity"):
        return False
    return True


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.
    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    database_url = settings.DATABASE_URL
    db_options = []
    if settings.DB_MIGRATION_LOCK_TIMEOUT:
        db_options.append("-c lock_timeout=%i" % settings.DB_MIGRATION_LOCK_TIMEOUT)
    if settings.DB_MIGRATION_STATEMENT_TIMEOUT:
        db_options.append("-c statement_timeout=%i" % settings.DB_MIGRATION_STATEMENT_TIMEOUT)
    connectable = create_engine(database_url, connect_args={"options": " ".join(db_options)})
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_object=include_object,
            include_schemas=True,
            transaction_per_migration=True,
        )
        if not settings.IS_DEV:
            connection.execute("UPDATE feature SET \"isActive\" = FALSE WHERE name = 'UPDATE_DISCOVERY_VIEW'")
        with context.begin_transaction():
            context.run_migrations()
        if not settings.IS_DEV:
            connection.execute("UPDATE feature SET \"isActive\" = TRUE WHERE name = 'UPDATE_DISCOVERY_VIEW'")


def run_migrations_for_tests() -> None:
    """Run migrations in a testing context"""
    database_url = settings.DATABASE_URL_TEST
    connectable = create_engine(database_url)
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_object=include_object,
            include_schemas=True,
            transaction_per_migration=False,
        )
        with context.begin_transaction():
            context.run_migrations()
