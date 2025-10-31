import logging

import click

import pcapi.utils.cron as cron_decorators
from pcapi.core.providers.titelive_bq_book_search import BigQueryProductSync
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
@cron_decorators.cron_require_feature(FeatureToggle.SYNCHRONIZE_TITELIVE_PRODUCTS_FROM_BIGQUERY_TABLES)
def synchronize_products_from_bigquery(batch_size: int) -> None:
    BigQueryProductSync().synchronize_products(batch_size)
