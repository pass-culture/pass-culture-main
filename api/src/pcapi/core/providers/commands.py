import datetime
import enum
import logging
from typing import Type

import click

import pcapi.core.providers.models as providers_models
import pcapi.core.providers.repository as providers_repository
import pcapi.utils.cron as cron_decorators
from pcapi.core.providers import allocine
from pcapi.local_providers import provider_manager
from pcapi.models import db
from pcapi.models.feature import FeatureToggle
from pcapi.utils import logging as logging_utils
from pcapi.utils.blueprint import Blueprint

from .etls.boost_etl import BoostExtractTransformLoadProcess
from .etls.cds_etl import CDSExtractTransformLoadProcess
from .etls.cgr_etl import CGRExtractTransformLoadProcess
from .titelive_book_search import TiteliveBookSearch
from .titelive_music_search import TiteliveMusicSearch
from .titelive_utils import generate_titelive_gtl_from_file


blueprint = Blueprint(__name__, __name__)
logger = logging.getLogger(__name__)


class CinemaProviders(enum.Enum):
    CGR = enum.auto()
    CINE_GROUP = enum.auto()
    CINE_OFFICE = enum.auto()


@blueprint.cli.command("synchronize_allocine_products")
@cron_decorators.cron_require_feature(FeatureToggle.ENABLE_RECURRENT_CRON)
def synchronize_allocine_products() -> None:
    allocine.synchronize_products()


@blueprint.cli.command("synchronize_provider_stocks")
@cron_decorators.log_cron_with_transaction
@cron_decorators.cron_require_feature(FeatureToggle.ENABLE_RECURRENT_CRON)
@click.argument("provider", type=click.Choice(CinemaProviders, case_sensitive=False), required=True)
def synchronize_provider_stocks(provider: CinemaProviders) -> None:
    """Fetch & load the cinema sessions of venues linked to given cinema provider"""
    CINEMA_PROVIDER_MAPPING: dict[
        CinemaProviders,
        tuple[
            str,
            Type[BoostExtractTransformLoadProcess]
            | Type[CDSExtractTransformLoadProcess]
            | Type[CGRExtractTransformLoadProcess],
        ],
    ] = {
        CinemaProviders.CGR: ("CGRStocks", CGRExtractTransformLoadProcess),
        CinemaProviders.CINE_GROUP: ("BoostStocks", BoostExtractTransformLoadProcess),
        CinemaProviders.CINE_OFFICE: ("CDSStocks", CDSExtractTransformLoadProcess),
    }

    local_class, ETLProcess = CINEMA_PROVIDER_MAPPING[provider]

    venue_providers = providers_repository.get_active_venue_providers_by_provider_local_class(local_class)
    for venue_provider in venue_providers:
        ETLProcess(venue_provider).execute()


@blueprint.cli.command("synchronize_venue_stocks")
@click.option("-vp", "--venue-provider-id", required=True, help="Venue provider id", type=int)
@click.option("--debug", is_flag=True)
def synchronize_venue_stocks(venue_provider_id: int, debug: bool = False) -> None:
    """Fetch & load the cinema sessions for given venue_provider"""
    _LOCAL_CLASS_NAME_TO_ETL_CLASS: dict[
        str,
        Type[BoostExtractTransformLoadProcess]
        | Type[CDSExtractTransformLoadProcess]
        | Type[CGRExtractTransformLoadProcess],
    ] = {
        "BoostStocks": BoostExtractTransformLoadProcess,
        "CDSStocks": CDSExtractTransformLoadProcess,
        "CGRStocks": CGRExtractTransformLoadProcess,
    }

    venue_provider: providers_models.VenueProvider = (
        db.session.query(providers_models.VenueProvider).filter_by(id=venue_provider_id).one()
    )

    if venue_provider.provider.localClass not in _LOCAL_CLASS_NAME_TO_ETL_CLASS:
        logger.info("The given venue provider is not linked to a cinema provider")
        return

    ETLProcess = _LOCAL_CLASS_NAME_TO_ETL_CLASS[venue_provider.provider.localClass]

    logging_level = logging.DEBUG if debug else logging.INFO
    with logging_utils.logging_at_level(logging.getLogger("pcapi"), logging_level):
        ETLProcess(venue_provider).execute()


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
