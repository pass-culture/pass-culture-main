from logging.config import fileConfig
import os

from alembic import context
from sqlalchemy import create_engine

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
from pcapi import settings
from pcapi.models.db import db


config = context.config
# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)
# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = db.metadata
# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.
def include_object(object, name, type_, reflected, compare_to) -> bool:  # pylint: disable=redefined-builtin
    # Don't generate DROP tables with autogenerate
    # https://alembic.sqlalchemy.org/en/latest/cookbook.html#don-t-generate-any-drop-table-directives-with-autogenerate
    if type_ == "table" and reflected and compare_to is None:
        return False
    if name in ("discovery_view", "discovery_view_v3", "transaction", "activity"):
        # TODO: flag discovery_view* as views:
        # https://alembic.sqlalchemy.org/en/latest/cookbook.html#don-t-emit-create-table-statements-for-views
        return False
    return True


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.
    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    database_url = os.environ.get("DATABASE_URL")
    db_options = []
    if settings.DB_MIGRATION_STATEMENT_TIMEOUT:
        db_options.append("-c statement_timeout=%i" % settings.DB_MIGRATION_STATEMENT_TIMEOUT)
    connectable = create_engine(database_url, connect_args={"options": " ".join(db_options)})
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_object=include_object,
            include_schemas=True,
            transaction_per_migration=False,
        )
        if not settings.IS_DEV:
            connection.execute("UPDATE feature SET \"isActive\" = FALSE WHERE name = 'UPDATE_DISCOVERY_VIEW'")
        with context.begin_transaction():
            context.run_migrations()
        if not settings.IS_DEV:
            connection.execute("UPDATE feature SET \"isActive\" = TRUE WHERE name = 'UPDATE_DISCOVERY_VIEW'")


def run_migrations_for_tests() -> None:
    """Run migrations in a testing context"""
    database_url = os.environ.get("DATABASE_URL_TEST")
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


if os.environ.get("RUN_ENV") == "tests":
    run_migrations_for_tests()
else:
    run_migrations_online()
