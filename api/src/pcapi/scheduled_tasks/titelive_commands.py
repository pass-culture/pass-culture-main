import datetime
import logging

import click

from pcapi.core.providers.titelive_book_search import TiteliveBookSearch
from pcapi.core.providers.titelive_music_search import TiteliveMusicSearch
from pcapi.models.feature import FeatureToggle
from pcapi.scheduled_tasks.decorators import cron_require_feature
from pcapi.scheduled_tasks.decorators import log_cron_with_transaction
from pcapi.utils.blueprint import Blueprint


logger = logging.getLogger(__name__)

blueprint = Blueprint(__name__, __name__)


@blueprint.cli.command("synchronize_titelive_music_products")
@click.option(
    "--from-date",
    help="sync music products that were modified after from_date (YYYY-MM-DD)",
    type=click.DateTime(),
    default=None,
)
@click.option(
    "--to-date",
    help="sync music products that were modified before to_date (YYYY-MM-DD)",
    type=click.DateTime(),
    default=None,
)
@click.option(
    "--from-page",
    help="page to sync from, defaults to 1",
    type=int,
    default=1,
)
@log_cron_with_transaction
@cron_require_feature(FeatureToggle.SYNCHRONIZE_TITELIVE_API_MUSIC_PRODUCTS)
def synchronize_titelive_music_products(
    from_date: datetime.datetime | None, to_date: datetime.datetime | None, from_page: int
) -> None:
    TiteliveMusicSearch().synchronize_products(
        from_date.date() if from_date else None, to_date.date() if to_date else None, from_page
    )


@blueprint.cli.command("synchronize_titelive_book_products")
@click.option(
    "--from-date",
    help="sync book products that were modified after from_date (YYYY-MM-DD)",
    type=click.DateTime(),
    default=None,
)
@click.option(
    "--to-date",
    help="sync music products that were modified before to_date (YYYY-MM-DD)",
    type=click.DateTime(),
    default=None,
)
@click.option(
    "--from-page",
    help="page to sync from, defaults to 1",
    type=int,
    default=1,
)
@log_cron_with_transaction
@cron_require_feature(FeatureToggle.SYNCHRONIZE_TITELIVE_PRODUCTS)
def synchronize_titelive_book_products(
    from_date: datetime.datetime | None, to_date: datetime.datetime | None, from_page: int
) -> None:
    TiteliveBookSearch().synchronize_products(
        from_date.date() if from_date else None, to_date.date() if to_date else None, from_page
    )
