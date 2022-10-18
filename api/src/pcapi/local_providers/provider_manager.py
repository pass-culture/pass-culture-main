import logging
from typing import Callable

from urllib3 import exceptions as urllib3_exceptions

import pcapi.connectors.notion as notion_connector
from pcapi.core.providers.models import VenueProvider
import pcapi.core.providers.repository as providers_repository
from pcapi.infrastructure.repository.stock_provider import provider_api
import pcapi.local_providers
from pcapi.local_providers.provider_api import synchronize_provider_api
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


def synchronize_venue_providers_for_provider(provider_id: int, limit: int | None = None) -> None:
    venue_providers = providers_repository.get_active_venue_providers_by_provider(provider_id)
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
        assert venue_provider.provider.localClass in [
            "AllocineStocks",
            "CDSStocks",
        ], "Only AllocineStocks or CDSStocks should reach this code"
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
