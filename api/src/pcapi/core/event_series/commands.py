import logging

import click

import pcapi.utils.cron as cron_decorators
from pcapi.models.feature import FeatureToggle
from pcapi.utils.blueprint import Blueprint


blueprint = Blueprint(__name__, __name__)
logger = logging.getLogger(__name__)


@blueprint.cli.command("update_event_series_from_delta")
@click.option("--batch-size", type=int, default=100, help="Batch size for updates.")
@cron_decorators.cron_require_feature(FeatureToggle.SYNCHRONIZE_EVENT_SERIES_FROM_BIGQUERY_TABLES)
def update_event_series_from_delta(batch_size: int) -> None:
    NotImplementedError("Not implemented yet")
