import datetime
import logging
from collections.abc import Generator
from contextlib import contextmanager
from time import time
from typing import Type

import click

import pcapi.core.providers.models as providers_models
import pcapi.core.providers.repository as providers_repository
import pcapi.utils.cron as cron_decorators
from pcapi.core.providers import allocine
from pcapi.local_providers import provider_manager
from pcapi.models import db
from pcapi.models.feature import FeatureToggle
from pcapi.utils.blueprint import Blueprint

from .etls.boost_etl import BoostETLProcess
from .etls.cds_etl import CineDigitalServiceETLProcess
from .titelive_book_search import TiteliveBookSearch
from .titelive_music_search import TiteliveMusicSearch
from .titelive_utils import generate_titelive_gtl_from_file


blueprint = Blueprint(__name__, __name__)
logger = logging.getLogger(__name__)


@contextmanager
def _set_debug_level(target_logger: logging.Logger, level: int) -> Generator[None, None, None]:
    old_level = target_logger.level
    target_logger.setLevel(level)

    try:
        yield
    finally:
        target_logger.setLevel(old_level)


@blueprint.cli.command("synchronize_allocine_products")
@cron_decorators.cron_require_feature(FeatureToggle.ENABLE_RECURRENT_CRON)
def synchronize_allocine_products() -> None:
    allocine.synchronize_products()


# TODO (tcoudray-pass, 07/10/25): Remove this command once Boost has been migrated to new integration
@blueprint.cli.command("test_etl_integration")
@click.option("-vp", "--venue-provider-id", required=True, help="Venue provider id", type=int)
def test_etl_integration(venue_provider_id: int) -> None:
    venue_provider: providers_models.VenueProvider = (
        db.session.query(providers_models.VenueProvider).filter_by(id=venue_provider_id).one()
    )

    local_class_to_etl_mapping: dict[str, Type[BoostETLProcess] | Type[CineDigitalServiceETLProcess]] = {
        "BoostStocks": BoostETLProcess,
        "CDSStocks": CineDigitalServiceETLProcess,
    }

    if venue_provider.provider.localClass not in local_class_to_etl_mapping:
        logger.warning("ETL integration not available for %s", venue_provider.provider.localClass)
        return

    with _set_debug_level(logging.getLogger("pcapi"), level=logging.DEBUG):
        etl_class = local_class_to_etl_mapping[venue_provider.provider.localClass]
        etl_process = etl_class(venue_provider)
        etl_process.execute()


@blueprint.cli.command("debug_synchronize_venue_provider")
@click.option("-vp", "--venue-provider-id", required=True, help="Venue provider id", type=int)
def debug_synchronize_venue_provider(venue_provider_id: int) -> None:
    """
    Start synchronize_venue_provider with `pcapi` logger at DEBUG level
    """
    with _set_debug_level(logging.getLogger("pcapi"), level=logging.DEBUG):
        venue_provider: providers_models.VenueProvider = (
            db.session.query(providers_models.VenueProvider).filter_by(id=venue_provider_id).one()
        )

        if venue_provider.provider.localClass == "EMSStocks":
            assert venue_provider.venueIdAtOfferProvider  # to make mypy happy
            ems_cinema_details = providers_repository.get_ems_cinema_details(venue_provider.venueIdAtOfferProvider)
            target_version = ems_cinema_details.lastVersion - 1  # retry from previous version

            provider_manager.synchronize_ems_venue_provider(
                venue_provider=venue_provider, target_version=target_version
            )
            return

        provider_manager.synchronize_venue_provider(venue_provider=venue_provider)


@blueprint.cli.command("update_providables")
@click.option("-p", "--provider-name", help="Limit update to this provider name")
@click.option(
    "-l",
    "--limit",
    help="Limit update to n items per providerName/venueId" + " (for test purposes)",
    type=int,
    default=None,
)
@click.option("-w", "--venue-provider-id", type=int, help="Limit update to this venue provider id")
def update_providables(provider_name: str, venue_provider_id: int, limit: int) -> None:
    start = time()
    logger.info(
        "Starting update_providables with provider_name=%s and venue_provider_id=%s", provider_name, venue_provider_id
    )

    if (provider_name and venue_provider_id) or not (provider_name or venue_provider_id):
        raise ValueError("Call either with provider-name or venue-provider-id")

    if provider_name:
        provider_manager.synchronize_data_for_provider(provider_name, limit)

    if venue_provider_id:
        venue_provider = providers_repository.get_venue_provider_by_id(venue_provider_id)
        provider_manager.synchronize_venue_provider(venue_provider, limit)

    logger.info(
        "Finished update_providables with provider_name=%s and venue_provider_id=%s elapsed=%.2f",
        provider_name,
        venue_provider_id,
        time() - start,
    )


@blueprint.cli.command("update_providables_by_provider_id")
@click.option("-p", "--provider-id", required=True, help="Update providables for this provider", type=int)
@click.option(
    "-l", "--limit", help="Limit update to n items per venue provider" + " (for test purposes)", type=int, default=None
)
def update_providables_by_provider_id(provider_id: int, limit: int | None) -> None:
    venue_providers = providers_repository.get_active_venue_providers_by_provider(provider_id)
    provider_manager.synchronize_venue_providers(venue_providers, limit)


@blueprint.cli.command("synchronize_allocine_stocks")
@cron_decorators.log_cron_with_transaction
@cron_decorators.cron_require_feature(FeatureToggle.ENABLE_RECURRENT_CRON)
@cron_decorators.cron_require_feature(FeatureToggle.SYNCHRONIZE_ALLOCINE)
def synchronize_allocine_stocks() -> None:
    """Launch AlloCine synchronization."""
    allocine_stocks_provider = providers_repository.get_provider_by_local_class("AllocineStocks")
    assert allocine_stocks_provider  # helps mypy
    venue_providers = providers_repository.get_active_venue_providers_by_provider(allocine_stocks_provider.id)
    provider_manager.synchronize_venue_providers(venue_providers)


@blueprint.cli.command("synchronize_cine_office_stocks")
@cron_decorators.log_cron_with_transaction
@cron_decorators.cron_require_feature(FeatureToggle.ENABLE_RECURRENT_CRON)
@cron_decorators.cron_require_feature(FeatureToggle.ENABLE_CDS_IMPLEMENTATION)
def synchronize_cine_office_stocks() -> None:
    """Launch Cine Office synchronization."""
    cine_office_stocks_provider = providers_repository.get_provider_by_local_class("CDSStocks")
    assert cine_office_stocks_provider  # helps mypy
    venue_providers = providers_repository.get_active_venue_providers_by_provider(cine_office_stocks_provider.id)
    provider_manager.synchronize_venue_providers(venue_providers)


@blueprint.cli.command("synchronize_boost_stocks")
@cron_decorators.log_cron_with_transaction
@cron_decorators.cron_require_feature(FeatureToggle.ENABLE_RECURRENT_CRON)
@cron_decorators.cron_require_feature(FeatureToggle.ENABLE_BOOST_API_INTEGRATION)
def synchronize_boost_stocks() -> None:
    """Launch Boost synchronization."""
    boost_stocks_provider = providers_repository.get_provider_by_local_class("BoostStocks")
    assert boost_stocks_provider  # helps mypy
    venue_providers = providers_repository.get_active_venue_providers_by_provider(boost_stocks_provider.id)
    provider_manager.synchronize_venue_providers(venue_providers)


@blueprint.cli.command("synchronize_cgr_stocks")
@cron_decorators.log_cron_with_transaction
@cron_decorators.cron_require_feature(FeatureToggle.ENABLE_RECURRENT_CRON)
@cron_decorators.cron_require_feature(FeatureToggle.ENABLE_CGR_INTEGRATION)
def synchronize_cgr_stocks() -> None:
    """Launch CGR synchronization."""
    cgr_stocks_provider = providers_repository.get_provider_by_local_class("CGRStocks")
    assert cgr_stocks_provider  # helps mypy
    venue_providers = providers_repository.get_active_venue_providers_by_provider(cgr_stocks_provider.id)
    provider_manager.synchronize_venue_providers(venue_providers)


@blueprint.cli.command("synchronize_ems_stocks")
@cron_decorators.log_cron_with_transaction
@cron_decorators.cron_require_feature(FeatureToggle.ENABLE_RECURRENT_CRON)
@cron_decorators.cron_require_feature(FeatureToggle.ENABLE_EMS_INTEGRATION)
def synchronize_ems_stocks_on_schedule() -> None:
    """Launch EMS synchronization"""
    provider_manager.synchronize_ems_venue_providers(from_last_version=True)


@blueprint.cli.command("update_gtl")
@click.option("-f", "--file", required=True, help="CSV extract of GTL_2023.xlsx with tab as separator", type=str)
def update_gtl(file: str) -> None:
    generate_titelive_gtl_from_file(file)
    # TODO we can later automatically reindex only the offers for which the gtl changed


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
@cron_decorators.log_cron_with_transaction
@cron_decorators.cron_require_feature(FeatureToggle.SYNCHRONIZE_TITELIVE_API_MUSIC_PRODUCTS)
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
@cron_decorators.log_cron_with_transaction
@cron_decorators.cron_require_feature(FeatureToggle.SYNCHRONIZE_TITELIVE_PRODUCTS)
def synchronize_titelive_book_products(
    from_date: datetime.datetime | None, to_date: datetime.datetime | None, from_page: int
) -> None:
    TiteliveBookSearch().synchronize_products(
        from_date.date() if from_date else None, to_date.date() if to_date else None, from_page
    )
