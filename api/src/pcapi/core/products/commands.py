import datetime
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
    "--from-date",
    help="Synchronise les produits modifiés depuis cette date (YYYY-MM-DD HH:MM:SS)",
    type=click.DateTime(),
    default=None,
)
@click.option(
    "--to-date",
    help="Synchronise les produits modifiés jusqu'à cette date (YYYY-MM-DD HH:MM:SS)",
    type=click.DateTime(),
    default=None,
)
@cron_decorators.log_cron_with_transaction
@cron_decorators.cron_require_feature(FeatureToggle.SYNCHRONIZE_TITELIVE_PRODUCTS_FROM_BIGQUERY_TABLES)
def synchronize_products_from_bigquery(
    from_date: datetime.datetime | None = None, to_date: datetime.datetime | None = None
) -> None:
    BigQueryProductSync().synchronize_products(
        from_date.date() if from_date else None, to_date.date() if to_date else None
    )
