from . import exceptions
from . import models as provider_models
from . import repository


def check_ticketing_urls_are_coherently_set(external_booking_url: str | None, external_cancel_url: str | None) -> None:
    both_set = external_booking_url is not None and external_cancel_url is not None
    both_unset = external_booking_url is None and external_cancel_url is None

    if not (both_set or both_unset):
        raise exceptions.TicketingUrlsMustBeBothSet()

    return


def check_ticketing_urls_can_be_unset(provider: provider_models.Provider) -> None:
    future_events_requiring_ticketing_systems = repository.get_future_events_requiring_provider_ticketing_system(
        provider
    )
    if future_events_requiring_ticketing_systems:
        raise exceptions.TicketingUrlsCannotBeUnset(
            blocking_events_ids=[event.id for event in future_events_requiring_ticketing_systems]
        )

    return
