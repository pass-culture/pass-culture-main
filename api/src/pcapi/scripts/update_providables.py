import logging
from time import time

import click

import pcapi.core.providers.repository as providers_repository
from pcapi.local_providers.provider_manager import synchronize_data_for_provider
from pcapi.local_providers.provider_manager import synchronize_venue_provider
from pcapi.local_providers.provider_manager import synchronize_venue_providers_for_provider
from pcapi.utils.blueprint import Blueprint


blueprint = Blueprint(__name__, __name__)
logger = logging.getLogger(__name__)


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
def update_providables(provider_name: str, venue_provider_id: int, limit: int):  # type: ignore [no-untyped-def]
    start = time()
    logger.info(
        "Starting update_providables with provider_name=%s and venue_provider_id=%s", provider_name, venue_provider_id
    )

    if (provider_name and venue_provider_id) or not (provider_name or venue_provider_id):
        raise ValueError("Call either with provider-name or venue-provider-id")

    if provider_name:
        synchronize_data_for_provider(provider_name, limit)

    if venue_provider_id:
        venue_provider = providers_repository.get_venue_provider_by_id(venue_provider_id)
        synchronize_venue_provider(venue_provider, limit)

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
def update_providables_by_provider_id(provider_id: int, limit: int) -> None:
    synchronize_venue_providers_for_provider(provider_id, limit)
