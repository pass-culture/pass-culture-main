from logging.config import fileConfig

from alembic import context

from pcapi.alembic.run_migrations import run_migrations
from pcapi.models import install_models


# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config
# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name, disable_existing_loggers=False)

install_models()
run_migrations()
