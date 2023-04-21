from pcapi.core.events.backend import ExternalServiceBackend

from pcapi.utils.module_loading import import_string

from . import Event
from . import config


def dispatch(event: Event) -> None:
    if event.name not in config.EVENTS_DISPATCHING:
        raise ValueError(f"Unknown event {event.name}")

    event_dispatching = config.EVENTS_DISPATCHING[event.name]
    for service in event_dispatching["services"]:
        backend: ExternalServiceBackend = import_string(service)()
        if event.name in config.LEGACY_EVENTS_TRANSLATION and service in config.LEGACY_EVENTS_TRANSLATION[event.name]:
            event.legacy_name = config.LEGACY_EVENTS_TRANSLATION[event.name][service].value
        backend.handle_event(event)
