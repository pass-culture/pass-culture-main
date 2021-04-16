import subprocess
from typing import Optional

from pcapi.core.offerers.models import Venue
from pcapi.core.providers.models import Provider
from pcapi.core.providers.models import VenueProvider
from pcapi.core.providers.repository import get_provider_enabled_for_pro_by_id
from pcapi.infrastructure.container import api_fnac_stocks
from pcapi.infrastructure.container import api_libraires_stocks
from pcapi.infrastructure.container import api_praxiel_stocks
from pcapi.infrastructure.container import api_titelive_stocks
from pcapi.local_providers.provider_api import synchronize_provider_api
from pcapi.models import ApiErrors
from pcapi.models.feature import FeatureToggle
from pcapi.repository import feature_queries
from pcapi.repository import repository
from pcapi.repository.venue_queries import find_by_id
from pcapi.routes.serialization.venue_provider_serialize import PostVenueProviderBody
from pcapi.use_cases.connect_venue_to_allocine import connect_venue_to_allocine
from pcapi.utils.human_ids import dehumanize
from pcapi.validation.routes.venue_providers import check_existing_provider
from pcapi.validation.routes.venues import check_existing_venue
from pcapi.workers.venue_provider_job import venue_provider_job


def create_venue_provider(venue_provider: PostVenueProviderBody) -> VenueProvider:
    provider_id = dehumanize(venue_provider.providerId)
    provider = get_provider_enabled_for_pro_by_id(provider_id)
    check_existing_provider(provider)

    venue_id = dehumanize(venue_provider.venueId)
    venue = find_by_id(venue_id)
    check_existing_venue(venue)

    if provider.localClass == "AllocineStocks":
        new_venue_provider = connect_venue_to_allocine(venue, venue_provider)
    else:
        new_venue_provider = connect_venue_to_provider(venue, provider, venue_provider.venueIdAtOfferProvider)

    _run_first_synchronization(new_venue_provider)

    return new_venue_provider


def _run_first_synchronization(new_venue_provider: VenueProvider) -> None:
    if not feature_queries.is_active(FeatureToggle.SYNCHRONIZE_VENUE_PROVIDER_IN_WORKER):
        subprocess.Popen(
            [
                "python",
                "src/pcapi/scripts/pc.py",
                "update_providables",
                "--venue-provider-id",
                str(new_venue_provider.id),
            ]
        )
        return

    venue_provider_job.delay(new_venue_provider.id)


SPECIFIC_STOCK_PROVIDER = {
    "LibrairesStocks": api_libraires_stocks,
    "FnacStocks": api_fnac_stocks,
    "TiteLiveStocks": api_titelive_stocks,
    "PraxielStocks": api_praxiel_stocks,
}
ERROR_CODE_PROVIDER_NOT_SUPPORTED = 400
ERROR_CODE_SIRET_NOT_SUPPORTED = 422


def connect_venue_to_provider(venue: Venue, provider: Provider, venueIdAtOfferProvider: str = None) -> VenueProvider:
    id_at_provider = venueIdAtOfferProvider or venue.siret
    _check_provider_can_be_used(provider)
    _check_venue_can_be_synchronized_with_provider(id_at_provider, provider)

    venue_provider = VenueProvider()
    venue_provider.venue = venue
    venue_provider.provider = provider
    venue_provider.venueIdAtOfferProvider = id_at_provider

    repository.save(venue_provider)
    return venue_provider


def _check_provider_can_be_used(
    provider: Provider,
) -> None:
    if not provider.implements_provider_api and provider.localClass not in SPECIFIC_STOCK_PROVIDER:
        api_errors = ApiErrors()
        api_errors.status_code = ERROR_CODE_PROVIDER_NOT_SUPPORTED
        api_errors.add_error("provider", "Provider non pris en charge")
        raise api_errors


def _check_venue_can_be_synchronized_with_provider(
    id_at_provider: str,
    provider: Provider,
) -> None:
    if not _siret_can_be_synchronized(id_at_provider, provider):
        api_errors = ApiErrors()
        api_errors.status_code = ERROR_CODE_SIRET_NOT_SUPPORTED
        api_errors.add_error("provider", _get_synchronization_error_message(provider.name, id_at_provider))
        raise api_errors


def _siret_can_be_synchronized(
    id_at_provider: str,
    provider: Provider,
) -> bool:
    if not id_at_provider:
        return False

    if provider.implements_provider_api:
        return synchronize_provider_api.check_siret_can_be_synchronized(id_at_provider, provider)
    return SPECIFIC_STOCK_PROVIDER[provider.localClass].can_be_synchronized(id_at_provider)


def _get_synchronization_error_message(provider_name: str, siret: Optional[str]) -> str:
    if siret:
        return f"L’importation d’offres avec {provider_name} n’est pas disponible pour le SIRET {siret}"
    return f"L’importation d’offres avec {provider_name} n’est pas disponible sans SIRET associé au lieu. Ajoutez un SIRET pour pouvoir importer les offres."
