import traceback
from typing import Callable, Optional

import local_providers
from local_providers.local_provider import LocalProvider
from repository import repository
from repository.provider_queries import get_provider_by_id
from repository.venue_provider_queries import get_venue_provider_by_id, get_active_venue_providers_for_specific_provider
from scheduled_tasks.logger import build_cron_log_message, CronStatus
from utils.logger import logger


def synchronize_data_for_provider(provider_name: str, limit: Optional[int] = None) -> None:
    provider_class = get_local_provider_class_by_name(provider_name)
    try:
        provider = provider_class()
        do_update(provider, limit)
    except Exception:
        formatted_traceback = traceback.format_exc()
        logger.error(build_cron_log_message(name=provider_name,
                                            status=CronStatus.FAILED,
                                            traceback=formatted_traceback))


def synchronize_venue_providers_for_provider(provider_id: int, limit: Optional[int] = None) -> None:
    venue_providers = get_active_venue_providers_for_specific_provider(provider_id)
    provider = get_provider_by_id(provider_id)
    provider_class = get_local_provider_class_by_name(provider.localClass)
    for venue_provider in venue_providers:
        provider = provider_class(venue_provider)
        do_update(provider, limit)


def do_update(provider: LocalProvider, limit: Optional[int]):
    try:
        provider.updateObjects(limit)
    except Exception:
        _remove_worker_id_after_venue_provider_sync_error(provider)
        formatted_traceback = traceback.format_exc()
        logger.error(build_cron_log_message(name=provider.__class__.__name__,
                                            status=CronStatus.STARTED,
                                            traceback=formatted_traceback))


def _remove_worker_id_after_venue_provider_sync_error(provider: LocalProvider):
    venue_provider_in_sync = provider.venue_provider
    if venue_provider_in_sync is not None:
        venue_provider_in_sync.syncWorkerId = None
        repository.save(venue_provider_in_sync)


def get_local_provider_class_by_name(class_name: str) -> Callable:
    return getattr(local_providers, class_name)


def synchronize_venue_provider(venue_provider_id: str, limit: Optional[int] = None):
    venue_provider = get_venue_provider_by_id(int(venue_provider_id))
    provider_class = get_local_provider_class_by_name(venue_provider.provider.localClass)
    provider = provider_class(venue_provider)
    do_update(provider, limit)
