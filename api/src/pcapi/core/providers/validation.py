from pcapi.core.offerers import models as offerers_models

from . import exceptions
from . import models as provider_models
from . import repository


def check_ticketing_urls_are_coherently_set(external_booking_url: str | None, external_cancel_url: str | None) -> None:
    both_set = external_booking_url is not None and external_cancel_url is not None
    both_unset = external_booking_url is None and external_cancel_url is None

    if not (both_set or both_unset):
        raise exceptions.ProviderException(
            {"ticketing_urls": ["Your `booking_url` and `cancel_url` must be either both set or both unset"]}
        )


def check_ticketing_urls_can_be_unset(
    provider: provider_models.Provider,
    venue: offerers_models.Venue | None = None,
) -> None:
    future_events_requiring_ticketing_systems = repository.get_future_events_requiring_ticketing_system(provider, venue)
    if future_events_requiring_ticketing_systems:
        raise exceptions.ProviderException(
            {
                "ticketing_urls": [
                    f"You cannot unset your `booking_url` and `cancel_url` because you have event(s) with stocks linked to your ticketing system. Blocking event ids: {[event.id for event in future_events_requiring_ticketing_systems]}"
                ]
            }
        )
