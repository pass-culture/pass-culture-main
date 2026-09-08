import enum
import logging
from time import time

import click

import pcapi.core.providers.repository as providers_repository
import pcapi.utils.cron as cron_decorators
from pcapi.connectors.ems import EMSScheduleConnector
from pcapi.core.providers import allocine
from pcapi.local_providers import provider_manager
from pcapi.models.feature import FeatureToggle
from pcapi.utils.blueprint import Blueprint

from .etls.boost_etl import BoostExtractTransformLoadProcess
from .etls.cgr_etl import CGRExtractTransformLoadProcess
from .etls.cine_office_etl import CineOfficeExtractTransformLoadProcess
from .etls.ems_etl import EMSExtractTransformLoadProcess
from .titelive_utils import generate_titelive_gtl_from_file


blueprint = Blueprint(__name__, __name__)
logger = logging.getLogger(__name__)


class CinemaLocalClasses(enum.StrEnum):
    CDSStocks = "CDSStocks"
    CGRStocks = "CGRStocks"
    BoostStocks = "BoostStocks"
    EMSStocks = "EMSStocks"


_LOCAL_CLASS_NAME_TO_ETL_CLASS: dict[
    str,
    type[BoostExtractTransformLoadProcess]
    | type[CineOfficeExtractTransformLoadProcess]
    | type[CGRExtractTransformLoadProcess],
] = {
    "BoostStocks": BoostExtractTransformLoadProcess,
    "CDSStocks": CineOfficeExtractTransformLoadProcess,  # INFO: CDS is the old name of CineOffice
    "CGRStocks": CGRExtractTransformLoadProcess,
}


@blueprint.cli.command("synchronize_allocine_products")
@cron_decorators.log_cron_with_transaction
@cron_decorators.cron_require_feature(FeatureToggle.ENABLE_RECURRENT_CRON)
@cron_decorators.cron_require_feature(FeatureToggle.SYNCHRONIZE_ALLOCINE_PRODUCTS)
def synchronize_allocine_products() -> None:
    allocine.synchronize_products()


@blueprint.cli.command("synchronize_allocine_products_with_bigquery")
@cron_decorators.log_cron_with_transaction
@cron_decorators.cron_require_feature(FeatureToggle.ENABLE_RECURRENT_CRON)
@cron_decorators.cron_require_feature(FeatureToggle.SYNCHRONIZE_ALLOCINE_PRODUCTS_FROM_BIGQUERY_TABLES)
def synchronize_allocine_products_with_bigquery() -> None:
    allocine.synchronize_products_with_bigquery()


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


# (tcoudray-pass, 7/9/26) TODO: Temporary private function
# To be removed when `synchronize_boost_stocks`, `synchronize_cgr_stocks` and `synchronize_cine_office_stocks`
# are replaced with `synchronize_cinema_provider_offers` (PC-43579)
def _synchronize_cinema_provider_offers(local_class: CinemaLocalClasses) -> None:
    ETLClass = _LOCAL_CLASS_NAME_TO_ETL_CLASS[local_class]
    cinema_provider = providers_repository.get_cinema_provider_by_local_class(local_class)
    venue_providers = providers_repository.get_active_venue_providers_by_provider(cinema_provider.id)

    for venue_provider in venue_providers:
        try:
            ETLClass(venue_provider).execute()
        except Exception as exception:
            # we except all exceptions to prevent that
            # one faulty venue blocks the synchronisation
            # of other venues
            logger.warning(
                "Error while synchronizing cinema venue",
                extra={
                    "venue_provider_id": venue_provider.id,
                    "venue_id": venue_provider.venueId,
                    "provider_id": venue_provider.providerId,
                    "exc": exception,
                },
            )


@blueprint.cli.command("synchronize_cinema_provider_offers")
@cron_decorators.log_cron_with_transaction
@cron_decorators.cron_require_feature(FeatureToggle.ENABLE_RECURRENT_CRON)
@click.argument("local_class", type=click.Choice(CinemaLocalClasses, case_sensitive=False), required=True)
def synchronize_cinema_provider_offers(local_class: CinemaLocalClasses) -> None:
    _synchronize_cinema_provider_offers(local_class)


# (tcoudray-pass, 7/9/26) TODO: To be replaced with `synchronize_cinema_provider_offers` (PC-43579)
@blueprint.cli.command("synchronize_cine_office_stocks")
@cron_decorators.log_cron_with_transaction
@cron_decorators.cron_require_feature(FeatureToggle.ENABLE_RECURRENT_CRON)
@cron_decorators.cron_require_feature(FeatureToggle.ENABLE_CDS_IMPLEMENTATION)
def synchronize_cine_office_stocks() -> None:
    """Launch Ciné Office synchronization."""
    if FeatureToggle.WIP_ENABLE_ETL_SYNC.is_active():
        _synchronize_cinema_provider_offers(CinemaLocalClasses.CDSStocks)
        return

    cine_office_stocks_provider = providers_repository.get_provider_by_local_class("CDSStocks")
    assert cine_office_stocks_provider  # helps mypy
    venue_providers = providers_repository.get_active_venue_providers_by_provider(cine_office_stocks_provider.id)
    provider_manager.synchronize_venue_providers(venue_providers)


# (tcoudray-pass, 7/9/26) TODO: To be replaced with `synchronize_cinema_provider_offers` (PC-43579)
@blueprint.cli.command("synchronize_boost_stocks")
@cron_decorators.log_cron_with_transaction
@cron_decorators.cron_require_feature(FeatureToggle.ENABLE_RECURRENT_CRON)
@cron_decorators.cron_require_feature(FeatureToggle.ENABLE_BOOST_API_INTEGRATION)
def synchronize_boost_stocks() -> None:
    """Launch Boost synchronization."""
    if FeatureToggle.WIP_ENABLE_ETL_SYNC.is_active():
        _synchronize_cinema_provider_offers(CinemaLocalClasses.BoostStocks)
        return

    boost_stocks_provider = providers_repository.get_provider_by_local_class("BoostStocks")
    assert boost_stocks_provider  # helps mypy
    venue_providers = providers_repository.get_active_venue_providers_by_provider(boost_stocks_provider.id)
    provider_manager.synchronize_venue_providers(venue_providers)


# (tcoudray-pass, 7/9/26) TODO: To be replaced with `synchronize_cinema_provider_offers` (PC-43579)
@blueprint.cli.command("synchronize_cgr_stocks")
@cron_decorators.log_cron_with_transaction
@cron_decorators.cron_require_feature(FeatureToggle.ENABLE_RECURRENT_CRON)
@cron_decorators.cron_require_feature(FeatureToggle.ENABLE_CGR_INTEGRATION)
def synchronize_cgr_stocks() -> None:
    """Launch CGR synchronization."""
    if FeatureToggle.WIP_ENABLE_ETL_SYNC.is_active():
        _synchronize_cinema_provider_offers(CinemaLocalClasses.CGRStocks)
        return

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
    if FeatureToggle.WIP_ENABLE_ETL_SYNC.is_active():
        cinema_provider = providers_repository.get_cinema_provider_by_local_class("EMSStocks")
        venue_providers = providers_repository.get_active_venue_providers_by_provider(cinema_provider.id)

        ems_connector = EMSScheduleConnector()
        # we fetch the schedules once and not inside the ETL process
        # for there is no endpoint to fetch the schedules for only
        # one cinema.
        schedules = ems_connector.get_schedules()

        for venue_provider in venue_providers:
            try:
                EMSExtractTransformLoadProcess(venue_provider).with_schedules_data(schedules).execute()
            except Exception as exception:
                # we except all exceptions to prevent that
                # one faulty venue blocks the synchronisation
                # of other venues
                logger.warning(
                    "Error while synchronizing cinema venue",
                    extra={
                        "venue_provider_id": venue_provider.id,
                        "venue_id": venue_provider.venueId,
                        "provider_id": venue_provider.providerId,
                        "exc": exception,
                    },
                )
        return

    provider_manager.synchronize_ems_venue_providers(from_last_version=True)


@blueprint.cli.command("update_gtl")
@click.option("-f", "--file", required=True, help="CSV extract of GTL_2023.xlsx with tab as separator", type=str)
def update_gtl(file: str) -> None:
    generate_titelive_gtl_from_file(file)
    # TODO we can later automatically reindex only the offers for which the gtl changed
