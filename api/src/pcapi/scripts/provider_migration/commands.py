import logging

import click

from pcapi.scripts.provider_migration import migrate_venue_provider
from pcapi.utils.blueprint import Blueprint


logger = logging.getLogger(__name__)
blueprint = Blueprint(__name__, __name__)


@blueprint.cli.command("execute_scheduled_venue_provider_migration")
@click.option(
    "-d",
    "--date_and_hour",
    help="Target date and hour in following format `%d/%m/%y_%HH` (for instance: `07/10/24_10H`)",
)
def execute_scheduled_venue_provider_migration(date_and_hour: str | None) -> None:
    """
    Normally, `date_and_hour` param should not be used as `target_day` and `target_hour`
    should be based on the actual time the command is called.
    `date_and_hour` is here in case we need to rerun a migration we missed.
    """
    if date_and_hour:
        date_and_hour_tuple = date_and_hour.split("_")
        if len(date_and_hour_tuple) != 2:
            logger.error(
                "Incorrect `date_and_hour` argument. Expected format:`%d/%m/%y_%HH` (for instance: `07/10/24_10H`)"
            )
            return
        target_day, targe_hour = date_and_hour_tuple
    else:
        target_day, targe_hour = migrate_venue_provider.get_migration_date_and_hour_keys()

    migrate_venue_provider.execute_scheduled_venue_provider_migration(target_day=target_day, target_hour=targe_hour)
