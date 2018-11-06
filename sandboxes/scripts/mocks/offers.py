""" offers """
from sandboxes.scripts.mocks.events import ALL_TYPED_EVENT_MOCKS
from sandboxes.scripts.mocks.things import ALL_TYPED_THING_MOCKS
from sandboxes.scripts.mocks.venues import ALL_VENUE_MOCKS
from sandboxes.scripts.mocks.utils.generators import get_all_typed_event_offer_mocks, \
                                                     get_all_typed_thing_offer_mocks
from utils.human_ids import humanize

OFFER_MOCKS = []

ALL_TYPED_EVENT_OFFER_MOCKS = get_all_typed_event_offer_mocks(
    ALL_TYPED_EVENT_MOCKS,
    ALL_VENUE_MOCKS
)
ALL_TYPED_THING_OFFER_MOCKS = get_all_typed_thing_offer_mocks(
    ALL_TYPED_THING_MOCKS,
    ALL_VENUE_MOCKS
)
ALL_TYPED_OFFER_MOCKS = ALL_TYPED_EVENT_OFFER_MOCKS + ALL_TYPED_THING_OFFER_MOCKS
OFFER_MOCKS += ALL_TYPED_OFFER_MOCKS

SCRATCH_OFFER_MOCKS = [
    {
        "eventId": humanize(0), # Rencontre avec Franck Lepage
        "id": humanize(0),
        "isActive": True,
        "venueId": humanize(0) # LE GRAND REX PARIS
    },
    {
        "eventId": humanize(1), # Concert de Gael Faye
        "id": humanize(1),
        "isActive": True,
        "venueId": humanize(2) # THEATRE DE L ODEON
    },
    {
        "eventId": humanize(2), # PNL chante Marx
        "id": humanize(2),
        "isActive": True,
        "venueId": humanize(2) # THEATRE DE L ODEON
    },
    {
        "id": humanize(3),
        "isActive": True,
        "thingId": humanize(0), # Ravage
        "venueId": humanize(2) # THEATRE DE L ODEON
    },
    {
        "id": humanize(4),
        "isActive": True,
        "thingId": humanize(1), # Le Monde Diplomatique
        "venueId": humanize(3) # THEATRE DE L ODEON (OL)
    }
]
OFFER_MOCKS += SCRATCH_OFFER_MOCKS
