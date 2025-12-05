import logging

import click

import pcapi.utils.cron as cron_decorators
from pcapi.core.providers.titelive_bq_book_search import BigQueryTiteliveBookProductSync
from pcapi.core.providers.titelive_bq_music_search import BigQueryTiteliveMusicProductSync
from pcapi.models.feature import FeatureToggle
from pcapi.utils.blueprint import Blueprint


blueprint = Blueprint(__name__, __name__)
logger = logging.getLogger(__name__)


@blueprint.cli.command("synchronize_titelive_book_products_from_bigquery")
@click.option(
    "--batch-size",
    help="Batch size for processing products.",
    type=click.INT,
    default=100,
    show_default=True,
)
@cron_decorators.log_cron_with_transaction
@cron_decorators.cron_require_feature(FeatureToggle.SYNCHRONIZE_TITELIVE_BOOK_PRODUCTS_FROM_BIGQUERY_TABLES)
def synchronize_titelive_book_products_from_bigquery(batch_size: int) -> None:
    BigQueryTiteliveBookProductSync().synchronize_products(batch_size)


@blueprint.cli.command("synchronize_titelive_music_products_from_bigquery")
@click.option(
    "--batch-size",
    help="Batch size for processing products.",
    type=click.INT,
    default=100,
    show_default=True,
)
@cron_decorators.log_cron_with_transaction
@cron_decorators.cron_require_feature(FeatureToggle.SYNCHRONIZE_TITELIVE_MUSIC_PRODUCTS_FROM_BIGQUERY_TABLES)
def synchronize_titelive_music_products_from_bigquery(batch_size: int) -> None:
    BigQueryTiteliveMusicProductSync().synchronize_products(batch_size)
