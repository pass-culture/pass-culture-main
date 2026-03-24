import functools
from typing import Any
from typing import Callable

from pcapi.core.providers import repository as providers_repository
from pcapi.core.providers.models import LocalProviderEvent
from pcapi.core.providers.models import LocalProviderEventType
from pcapi.core.providers.models import Provider
from pcapi.models import db
from pcapi.utils import date as date_utils
from pcapi.utils.transaction_manager import atomic


def _log_sync_status(
    provider: Provider, event_type: LocalProviderEventType, message: str | None = None
) -> LocalProviderEvent:
    return LocalProviderEvent(
        date=date_utils.get_naive_utc_now(),
        payload=message,
        provider=provider,
        type=event_type,
    )


def log_provider_synchronization(provider_name: str) -> Callable[[Callable], Callable]:
    """
    Decorator to log the synchronization status of a provider.

    This decorator wraps a synchronization function and logs events to the database
    tracking the start, successful completion, or failure of the process.

    Behavior:
    1. Logs a `SyncStart` event before the wrapped function execution.
    2. Executes the wrapped function.
    3. Logs a `SyncEnd` event if execution is successful.
    4. Logs a `SyncError` event with the exception name if an error occurs,
       then re-raises the exception.

    Args:
        provider_name (str): The name of the provider to log synchronization for.
            Must match a valid provider name in the system.

    Returns:
        Callable[[Callable], Callable]: The decorated function.
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            provider = providers_repository.get_provider_by_name(provider_name)
            try:
                with atomic():
                    db.session.add(_log_sync_status(provider, LocalProviderEventType.SyncStart))

                result = func(*args, **kwargs)

                with atomic():
                    db.session.add(_log_sync_status(provider, LocalProviderEventType.SyncEnd))
                return result

            except Exception as e:
                db.session.rollback()
                with atomic():
                    db.session.add(
                        _log_sync_status(
                            provider,
                            LocalProviderEventType.SyncError,
                            e.__class__.__name__,
                        )
                    )
                raise

        return wrapper

    return decorator
