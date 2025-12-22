"""
Alembic environment for TimescaleDB-specific migrations.

This environment runs migrations that are specific to TimescaleDB,
such as converting tables to hypertables.

It uses TIMESCALEDB_DATABASE_URL from environment or from .env.local.secret.
"""

import logging
import os
import sys
import time
import typing
from logging.config import fileConfig
from pathlib import Path

import sqlalchemy.exc
from alembic import context
from dotenv import load_dotenv
from sqlalchemy import create_engine

from pcapi import settings


load_dotenv(dotenv_path=Path(__file__).parents[3] / ".env.local.secret")


TIMESCALEDB_DATABASE_URL = os.environ.get("TIMESCALEDB_DATABASE_URL")
if not TIMESCALEDB_DATABASE_URL:
    sys.exit(
        "ERROR: TIMESCALEDB_DATABASE_URL environment variable is required.\n"
        "Add it to api/.env.local.secret or set it inline."
    )


logger = logging.getLogger(__name__)

config = context.config
if config.config_file_name:
    fileConfig(config.config_file_name, disable_existing_loggers=False)


def run_online_migrations() -> None:
    """Run migrations with a SQL connection."""
    if not TIMESCALEDB_DATABASE_URL:
        sys.exit(
            "ERROR: TIMESCALEDB_DATABASE_URL environment variable is required.\n"
            "Add it to api/.env.local.secret or set it inline."
        )

    db_options = []
    if settings.DB_MIGRATION_LOCK_TIMEOUT:
        db_options.append("-c lock_timeout=%i" % settings.DB_MIGRATION_LOCK_TIMEOUT)
    if settings.DB_MIGRATION_STATEMENT_TIMEOUT:
        db_options.append("-c statement_timeout=%i" % settings.DB_MIGRATION_STATEMENT_TIMEOUT)

    connectable = create_engine(
        TIMESCALEDB_DATABASE_URL,
        connect_args={"options": " ".join(db_options)},
    )
    logger.warning(
        "TimescaleDB Alembic will use TIMESCALEDB_DATABASE_URL: %s",
        TIMESCALEDB_DATABASE_URL.replace(":passq@", ":***@"),
    )
    logger.warning(
        "Connection settings: lock_timeout = %d ms, statement_timeout = %d ms",
        settings.DB_MIGRATION_LOCK_TIMEOUT,
        settings.DB_MIGRATION_STATEMENT_TIMEOUT,
    )

    attempt = 1
    success = False

    def reset_attempt(*args: typing.Any, **kwargs: typing.Any) -> None:
        nonlocal attempt
        attempt = 0

    while True:
        logger.warning(
            "Running TimescaleDB migrations: attempt %d/%d",
            attempt,
            settings.DB_MIGRATION_MAX_ATTEMPTS,
            extra={"attempt": attempt, "max_attempts": settings.DB_MIGRATION_MAX_ATTEMPTS},
        )

        try:
            with connectable.connect() as connection:
                context.configure(
                    connection=connection,
                    target_metadata=None,
                    include_schemas=True,
                    transaction_per_migration=True,
                    on_version_apply=reset_attempt,
                    version_table="alembic_version_timescaledb",
                )
                with context.begin_transaction():
                    context.run_migrations()
                    success = True
                    break

        except sqlalchemy.exc.OperationalError as exc:
            db_error = str(exc.orig).rstrip("\n")
            logger.warning("OperationalError: %s", db_error, extra={"exc": exc})
            db_statement = str(exc.statement).lstrip("\n")
            logger.warning("[SQL: %s]", db_statement)

            attempt += 1
            if attempt > settings.DB_MIGRATION_MAX_ATTEMPTS:
                sys.exit("FAILURE: TimescaleDB migrations failed to be run.")

            logger.warning("Retrying in %d seconds...", settings.DB_MIGRATION_RETRY_DELAY)
            time.sleep(settings.DB_MIGRATION_RETRY_DELAY)

    if success:
        logger.warning("SUCCESS: TimescaleDB migrations successfully run")


def run_offline_migrations() -> None:
    """Run migrations without a SQL connection."""
    context.configure(
        url=TIMESCALEDB_DATABASE_URL,
        literal_binds=True,
        transaction_per_migration=True,
        version_table="alembic_version_timescaledb",
    )
    context.run_migrations()


if context.is_offline_mode():
    run_offline_migrations()
else:
    run_online_migrations()
