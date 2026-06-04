import logging

import click

import pcapi.utils.cron as cron_decorators
from pcapi.connectors.big_query.importer.event_series import EventSeriesImporter
from pcapi.connectors.big_query.importer.event_series import EventSeriesOfferLinkImporter
from pcapi.connectors.big_query.queries.event_series import EventSeriesPreIngestionChecksQuery
from pcapi.models.feature import FeatureToggle
from pcapi.utils.blueprint import Blueprint


blueprint = Blueprint(__name__, __name__)
logger = logging.getLogger(__name__)


@blueprint.cli.command("update_event_series_from_delta")
@click.option("--batch-size", type=int, default=100, help="Batch size for updates.")
@cron_decorators.cron_require_feature(FeatureToggle.SYNCHRONIZE_EVENT_SERIES_FROM_BIGQUERY_TABLES)
def update_event_series_from_delta(batch_size: int) -> None:
    logger.info("Starting event series update from delta tables...")

    checks = next(EventSeriesPreIngestionChecksQuery().execute(), None)
    if checks is None or not checks.ready_for_ingestion:
        logger.warning("Data is not ready to be ingested. Skipping Event Series ingestion.")
        return

    logger.info("Event series data is ready to be ingested. Starting ingestion...")
    EventSeriesImporter().run_delta_update(batch_size)
    EventSeriesOfferLinkImporter().run_delta_update(batch_size)
    logger.info("Event series update from delta tables finished successfully.")
