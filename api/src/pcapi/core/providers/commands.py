import logging
from time import time

import click
import sqlalchemy as sa

from pcapi.core.providers import allocine
import pcapi.core.providers.repository as providers_repository
from pcapi.local_providers import provider_manager
from pcapi.utils.blueprint import Blueprint

from . import models
from . import tasks
from .titelive_utils import generate_titelive_gtl_from_file


blueprint = Blueprint(__name__, __name__)
logger = logging.getLogger(__name__)


@blueprint.cli.command("synchronize_allocine_products")
def synchronize_allocine_products() -> None:
    allocine.synchronize_products()


@blueprint.cli.command("synchronize_venue_providers_apis")
def synchronize_venue_providers_apis() -> None:
    _synchronize_venue_providers_apis()


def _synchronize_venue_providers_apis() -> None:
    providers_apis = (
        models.Provider.query.filter(
            models.Provider.isActive,
            models.Provider.apiUrl.is_not(None),
        )
        .join(models.Provider.venueProviders)
        .options(sa.orm.contains_eager(models.Provider.venueProviders))
        .all()
    )

    for provider in providers_apis:
        venue_provider_ids = [
            venue_provider.id for venue_provider in provider.venueProviders if venue_provider.isActive
        ]

        if provider.enableParallelSynchronization:
            for venue_provider_id in venue_provider_ids:
                logger.info(
                    "Enqueuing synchronization with parallel mode",
                    extra={"provider": provider.name, "venue_provider": venue_provider_id},
                )
                tasks.synchronize_venue_providers_task.delay(
                    tasks.SynchronizeVenueProvidersRequest(
                        provider_id=provider.id,
                        venue_provider_ids=[venue_provider_id],
                    )
                )
        else:
            logger.info(
                "Enqueuing synchronization without parallel mode",
                extra={"provider": provider.name, "venue_count": len(venue_provider_ids)},
            )
            tasks.synchronize_venue_providers_task.delay(
                tasks.SynchronizeVenueProvidersRequest(
                    provider_id=provider.id,
                    venue_provider_ids=venue_provider_ids,
                )
            )


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


@blueprint.cli.command("update_gtl")
@click.option("-f", "--file", required=True, help="CSV extract of GTL_2023.xlsx with tab as separator", type=str)
def update_gtl(file: str) -> None:
    generate_titelive_gtl_from_file(file)
    # TODO we can later automatically reindex only the offers for which the gtl changed
