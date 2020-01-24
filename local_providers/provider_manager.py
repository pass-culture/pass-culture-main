import traceback
from typing import Callable

import local_providers
from local_providers.local_provider import LocalProvider
from models import PcObject
from scripts.cron_logger.cron_logger import build_cron_log_message
from scripts.cron_logger.cron_status import CronStatus
from utils.logger import logger


def do_update(provider: LocalProvider, limit: int):
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
        PcObject.save(venue_provider_in_sync)


def get_local_provider_class_by_name(class_name: str) -> Callable:
    return getattr(local_providers, class_name)
