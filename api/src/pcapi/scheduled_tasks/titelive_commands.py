import datetime
import logging

import click

from pcapi.core.providers.titelive_book_search import TiteliveBookSearch
from pcapi.core.providers.titelive_music_search import TiteliveMusicSearch
from pcapi.local_providers.provider_manager import synchronize_data_for_provider
from pcapi.models.feature import FeatureToggle
from pcapi.scheduled_tasks.decorators import cron_require_feature
from pcapi.scheduled_tasks.decorators import log_cron_with_transaction
from pcapi.utils.blueprint import Blueprint


logger = logging.getLogger(__name__)

blueprint = Blueprint(__name__, __name__)


@blueprint.cli.command("synchronize_titelive_things")
@log_cron_with_transaction
@cron_require_feature(FeatureToggle.SYNCHRONIZE_TITELIVE_PRODUCTS)
def synchronize_titelive_things() -> None:
    """Launches Titelive products synchronization through TiteLiveThings provider"""
    if FeatureToggle.WIP_ENABLE_TITELIVE_API_FOR_BOOKS.is_active():
        logger.info(
            "FeatureToggle.WIP_ENABLE_TITELIVE_API_FOR_BOOKS is active. Use synchronize_titelive_book_products instead"
        )
        return
    synchronize_data_for_provider("TiteLiveThings")


@blueprint.cli.command("synchronize_titelive_thing_descriptions")
@log_cron_with_transaction
@cron_require_feature(FeatureToggle.SYNCHRONIZE_TITELIVE_PRODUCTS_DESCRIPTION)
def synchronize_titelive_thing_descriptions() -> None:
    """Launches Titelive descriptions synchronization through TiteLiveThingDescriptions provider"""
    if FeatureToggle.WIP_ENABLE_TITELIVE_API_FOR_BOOKS.is_active():
        logger.info(
            "FeatureToggle.WIP_ENABLE_TITELIVE_API_FOR_BOOKS is active. Use synchronize_titelive_book_products instead"
        )
        return
    synchronize_data_for_provider("TiteLiveThingDescriptions")


@blueprint.cli.command("synchronize_titelive_thing_thumbs")
@log_cron_with_transaction
@cron_require_feature(FeatureToggle.SYNCHRONIZE_TITELIVE_PRODUCTS_THUMBS)
def synchronize_titelive_thing_thumbs() -> None:
    """Launches Titelive thumbs synchronization through TiteLiveThingThumbs provider"""
    if FeatureToggle.WIP_ENABLE_TITELIVE_API_FOR_BOOKS.is_active():
        logger.info(
            "FeatureToggle.WIP_ENABLE_TITELIVE_API_FOR_BOOKS is active. Use synchronize_titelive_book_products instead"
        )
        return
    synchronize_data_for_provider("TiteLiveThingThumbs")


@blueprint.cli.command("synchronize_titelive_music_products")
@click.option(
    "--from-date",
    help="sync music products that were modified after from_date (YYYY-MM-DD)",
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
def synchronize_titelive_music_products(from_date: datetime.datetime | None, from_page: int) -> None:
    TiteliveMusicSearch().synchronize_products(from_date.date() if from_date else None, from_page)


@blueprint.cli.command("synchronize_titelive_book_products")
@click.option(
    "--from-date",
    help="sync book products that were modified after from_date (YYYY-MM-DD)",
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
@cron_require_feature(FeatureToggle.WIP_ENABLE_TITELIVE_API_FOR_BOOKS)
@cron_require_feature(FeatureToggle.SYNCHRONIZE_TITELIVE_PRODUCTS)
@cron_require_feature(FeatureToggle.SYNCHRONIZE_TITELIVE_PRODUCTS_DESCRIPTION)
@cron_require_feature(FeatureToggle.SYNCHRONIZE_TITELIVE_PRODUCTS_THUMBS)
def synchronize_titelive_book_products(from_date: datetime.datetime | None, from_page: int) -> None:
    # When removing WIP_ENABLE_TITELIVE_API_FOR_BOOKS, also remove the 3 crons above (# synchronize_titelive_things_*), they will be obsolete
    TiteliveBookSearch().synchronize_products(from_date.date() if from_date else None, from_page)
