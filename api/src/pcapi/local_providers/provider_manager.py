import logging
from typing import Callable

from urllib3 import exceptions as urllib3_exceptions

from pcapi.connectors import ems
import pcapi.connectors.notion as notion_connector
from pcapi.core.providers import repository as providers_repository
from pcapi.core.providers.constants import CINEMA_PROVIDER_NAMES
from pcapi.core.providers.models import VenueProvider
from pcapi.infrastructure.repository.stock_provider import provider_api
import pcapi.local_providers
from pcapi.local_providers.cinema_providers.ems.ems_stocks import EMSStocks
from pcapi.local_providers.provider_api import synchronize_provider_api
from pcapi.models import db
from pcapi.repository import transaction
from pcapi.scheduled_tasks.logger import CronStatus
from pcapi.scheduled_tasks.logger import build_cron_log_message
from pcapi.utils import requests


logger = logging.getLogger(__name__)


def synchronize_data_for_provider(provider_name: str, limit: int | None = None) -> None:
    provider_class = get_local_provider_class_by_name(provider_name)
    try:
        provider = provider_class()
        provider.updateObjects(limit)
    except Exception:  # pylint: disable=broad-except
        logger.exception(build_cron_log_message(name=provider_name, status=CronStatus.FAILED))


def synchronize_venue_providers(venue_providers: list[VenueProvider], limit: int | None = None) -> None:
    for venue_provider in venue_providers:
        log_data = {
            "venue_provider": venue_provider.id,
            "venue": venue_provider.venueId,
            "provider": venue_provider.providerId,
        }
        try:
            with transaction():
                synchronize_venue_provider(venue_provider, limit)
        except (urllib3_exceptions.HTTPError, requests.exceptions.RequestException) as exception:
            logger.error("Connexion error while synchronizing venue_provider", extra=log_data | {"exc": exception})
        except provider_api.ProviderAPIException as exception:
            notion_connector.add_to_synchronization_error_database(exception, venue_provider)
            logger.error(  # pylint: disable=logging-fstring-interpolation
                f"ProviderAPIException with code {exception.status_code} while synchronizing venue_provider",
                extra=log_data | {"exc": exception},
            )
        except Exception as exception:  # pylint: disable=broad-except
            notion_connector.add_to_synchronization_error_database(exception, venue_provider)
            logger.exception("Unexpected error while synchronizing venue provider", extra=log_data)


def get_local_provider_class_by_name(class_name: str) -> Callable:
    return getattr(pcapi.local_providers, class_name)


def synchronize_venue_provider(venue_provider: VenueProvider, limit: int | None = None) -> None:
    if venue_provider.provider.implements_provider_api and not venue_provider.provider.isCinemaProvider:
        synchronize_provider_api.synchronize_venue_provider(venue_provider)

    else:
        assert (
            venue_provider.provider.localClass
            in [
                "AllocineStocks",
            ]
            + CINEMA_PROVIDER_NAMES
        ), f"Only {', '.join(CINEMA_PROVIDER_NAMES)} or AllocineStocks should reach this code"
        provider_class = get_local_provider_class_by_name(venue_provider.provider.localClass)

        logger.info(
            "Starting synchronization of venue_provider=%s with provider=%s",
            venue_provider.id,
            venue_provider.provider.localClass,
        )
        provider = provider_class(venue_provider)
        provider.updateObjects(limit)
        logger.info(
            "Ended synchronization of venue_provider=%s with provider=%s",
            venue_provider.id,
            venue_provider.provider.localClass,
        )


def synchronize_ems_venue_providers(from_last_version: bool = False) -> None:
    venues_provider_to_sync: set[int] = set()
    venue_provider_by_site_id: dict[str, VenueProvider] = {}
    last_version = providers_repository.get_ems_oldest_sync_version() if from_last_version else 0
    logger.info("Starting EMS synchronization", extra={"version": last_version})
    cinemas_programs = ems.get_cinemas_programs(version=last_version)
    new_version = cinemas_programs.version
    ems_provider_id = providers_repository.get_provider_by_local_class("EMSStocks").id
    active_venues_provider = providers_repository.get_active_venue_providers_by_provider(ems_provider_id)

    for active_venue_provider in active_venues_provider:
        venue_provider_by_site_id[active_venue_provider.venueIdAtOfferProvider] = active_venue_provider
        venues_provider_to_sync.add(active_venue_provider.id)

    for site in cinemas_programs.sites:
        venue_provider = venue_provider_by_site_id.get(site.id)
        if not venue_provider:
            logger.info("Venue provider for EMS site id %s not found", site.id)
            continue
        log_data = {
            "venue_provider": venue_provider.id,
            "venue": venue_provider.venueId,
            "provider": venue_provider.providerId,
        }
        try:
            with transaction():
                ems_stocks = EMSStocks(venue_provider=venue_provider, site=site)
                ems_stocks.synchronize()
        except (urllib3_exceptions.HTTPError, requests.exceptions.RequestException) as exception:
            logger.error("Connexion error while synchronizing venue_provider", extra=log_data | {"exc": exception})
            venues_provider_to_sync.discard(venue_provider.id)
        except provider_api.ProviderAPIException as exception:
            notion_connector.add_to_synchronization_error_database(exception, venue_provider)
            logger.error(  # pylint: disable=logging-fstring-interpolation
                f"ProviderAPIException with code {exception.status_code} while synchronizing venue_provider",
                extra=log_data | {"exc": exception},
            )
            venues_provider_to_sync.discard(venue_provider.id)
        except Exception as exception:  # pylint: disable=broad-except
            notion_connector.add_to_synchronization_error_database(exception, venue_provider)
            logger.exception("Unexpected error while synchronizing venue provider", extra=log_data)
            venues_provider_to_sync.discard(venue_provider.id)

    with transaction():
        providers_repository.bump_ems_sync_version(new_version, venues_provider_to_sync)
        db.session.commit()


def synchronize_ems_venue_provider(venue_provider: VenueProvider) -> None:
    ems_cinema_details = providers_repository.get_ems_cinema_details(venue_provider.venueIdAtOfferProvider)
    last_version = ems_cinema_details.lastVersion
    cinemas_programs = ems.get_cinemas_programs(last_version)
    new_version = cinemas_programs.version
    for site in cinemas_programs.sites:
        if site.id != venue_provider.venueIdAtOfferProvider:
            continue
        ems_stocks = EMSStocks(venue_provider=venue_provider, site=site)
        ems_stocks.synchronize()
        providers_repository.bump_ems_sync_version(new_version, [venue_provider.id])
        db.session.commit()
