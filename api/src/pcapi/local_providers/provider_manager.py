import logging
from typing import Callable
from typing import Optional

from pcapi.core.providers.models import VenueProvider
import pcapi.local_providers
from pcapi.local_providers.local_provider import LocalProvider
from pcapi.local_providers.provider_api import synchronize_provider_api
from pcapi.repository.venue_provider_queries import get_active_venue_providers_for_specific_provider
from pcapi.scheduled_tasks.logger import CronStatus
from pcapi.scheduled_tasks.logger import build_cron_log_message


logger = logging.getLogger(__name__)


def synchronize_data_for_provider(provider_name: str, limit: Optional[int] = None) -> None:
    provider_class = get_local_provider_class_by_name(provider_name)
    try:
        provider = provider_class()
        do_update(provider, limit)
    except Exception:  # pylint: disable=broad-except
        logger.exception(build_cron_log_message(name=provider_name, status=CronStatus.FAILED))


def synchronize_venue_providers_for_provider(provider_id: int, limit: Optional[int] = None) -> None:
    venue_providers = get_active_venue_providers_for_specific_provider(provider_id)
    for venue_provider in venue_providers:
        synchronize_venue_provider(venue_provider, limit)


def do_update(provider: LocalProvider, limit: Optional[int]):
    try:
        provider.updateObjects(limit)
    except Exception:  # pylint: disable=broad-except
        logger.exception(build_cron_log_message(name=provider.__class__.__name__, status=CronStatus.STARTED))


def get_local_provider_class_by_name(class_name: str) -> Callable:
    return getattr(pcapi.local_providers, class_name)


def synchronize_venue_provider(venue_provider: VenueProvider, limit: Optional[int] = None):
    if venue_provider.provider.implements_provider_api:
        synchronize_provider_api.synchronize_venue_provider(venue_provider)

    else:
        assert venue_provider.provider.localClass == "AllocineStocks", "Only AllocineStocks should reach this code"
        provider_class = get_local_provider_class_by_name(venue_provider.provider.localClass)

        logger.info(
            "Starting synchronization of venue_provider=%s with provider=%s",
            venue_provider.id,
            venue_provider.provider.localClass,
        )
        try:
            provider = provider_class(venue_provider)
            do_update(provider, limit)
        except Exception:  # pylint: disable=broad-except
            logger.exception(build_cron_log_message(name=provider_class.__name__, status=CronStatus.FAILED))
        logger.info(
            "Ended synchronization of venue_provider=%s with provider=%s",
            venue_provider.id,
            venue_provider.provider.localClass,
        )
