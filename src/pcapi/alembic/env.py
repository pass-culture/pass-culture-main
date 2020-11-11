from __future__ import with_statement

from logging.config import fileConfig
import os

from alembic import context
from sqlalchemy import create_engine

from pcapi.models.db import db

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
from pcapi.utils.config import IS_DEV


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


def include_object(object, name, type_, reflected, compare_to):
    if type_ == "table" and name in ("transaction", "activity"):
        return False
    else:
        return True


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    database_url = os.environ.get("DATABASE_URL")
    connectable = create_engine(database_url)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_object=include_object,
            include_schemas=True,
            transaction_per_migration=False,
        )

        if not IS_DEV:
            connection.execute("UPDATE feature SET \"isActive\" = FALSE WHERE name = 'UPDATE_DISCOVERY_VIEW'")

        with context.begin_transaction():
            context.run_migrations()

        if not IS_DEV:
            connection.execute("UPDATE feature SET \"isActive\" = TRUE WHERE name = 'UPDATE_DISCOVERY_VIEW'")


def run_migrations_for_tests():
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
