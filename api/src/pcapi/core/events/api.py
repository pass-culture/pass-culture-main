import pcapi.core.events.backend as events_backend
from pcapi.utils.module_loading import import_string

from . import config


def dispatch(event: events_backend.Event) -> None:
    if event.name not in config.EVENTS_DISPATCHING:
        raise ValueError(f"Unknown event {event.name}")

    target_services = config.EVENTS_DISPATCHING.get(event.name, [])
    for service in target_services:
        backend: events_backend.ExternalServiceBackend = import_string(service)()
        backend.handle_event(event)
