import logging
import sys

import alembic.config
import alembic.runtime.migration
import alembic.script
import click
import sqlalchemy

from pcapi import settings
from pcapi.utils.blueprint import Blueprint


blueprint = Blueprint(__name__, __name__)


@blueprint.cli.command("check_pre_migrations")
@click.option(
    "--alembic-config-path",
    help="Path to Alembic configuration file",
    type=str,
    default="alembic.ini",
)
def check_pre_migrations(alembic_config_path: str) -> None:
    """Assert that pre-deployment migrations have been applied.

    It does NOT apply migrations.

    This command is used to prevent the deployment of code if
    pre-deployment migrations have not been applied.
    """
    assert settings.DATABASE_URL  # helps mypy
    engine = sqlalchemy.create_engine(settings.DATABASE_URL)
    with engine.begin() as connection:
        # Avoid useless INFO messages displayed by Alembic when setting up its context.
        alembic.runtime.migration.log.setLevel(logging.WARNING)
        context = alembic.runtime.migration.MigrationContext.configure(connection)
        config = alembic.config.Config(alembic_config_path)
        directory = alembic.script.ScriptDirectory.from_config(config)
        directory_pre_head_script = directory.get_revision("pre@head")
        assert directory_pre_head_script  # helps mypy
        directory_pre_head = directory_pre_head_script.revision
        database_pre_head = _get_database_pre_head(context.get_current_heads(), directory)
        if directory_pre_head != database_pre_head:
            sys.exit(
                f"ERR: Missing pre-deployment migrations: last revision is {directory_pre_head}, but database is at {database_pre_head}"
            )
    print("OK")


def _get_database_pre_head(
    heads: tuple[str, ...],
    directory: alembic.script.ScriptDirectory,
) -> str:
    for head in heads:
        script = directory.get_revision(head)
        assert script  # helps mypy
        if "pre" in script.branch_labels:
            return head
    raise ValueError(f"Could not find any of {heads} in migrations directory")
