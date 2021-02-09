from logging.config import fileConfig

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
from pcapi import settings
from pcapi.alembic.run_migrations import run_migrations_for_tests
from pcapi.alembic.run_migrations import run_migrations_online


config = context.config
# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)

if settings.IS_RUNNING_TESTS:
    run_migrations_for_tests()
else:
    run_migrations_online()
