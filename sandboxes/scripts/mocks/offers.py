""" offers """
from sandboxes.scripts.mocks.events import ALL_TYPED_EVENT_MOCKS
from sandboxes.scripts.mocks.things import ALL_TYPED_THING_MOCKS
from sandboxes.scripts.mocks.venues import ALL_VENUE_MOCKS
from sandboxes.scripts.mocks.utils.generators import get_all_typed_event_offer_mocks, \
                                                     get_all_typed_thing_offer_mocks

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
        "eventKey": "d33ee240-dc59-11e8-a29f-0242ac130000", # Rencontre avec Franck Lepage
        "isActive": True,
        "key": "d33ee240-dc59-11e8-a29f-0242ac130000",
        "venueKey": "d33ee240-dc59-11e8-a29f-0242ac130002" # LE GRAND REX PARIS
    },
    {
        "eventKey": "d33ee240-dc59-11e8-a29f-0242ac130000", # Rencontre avec Franck Lepage
        "isActive": True,
        "key": "d33ee240-dc59-11e8-a29f-0242ac130001",
        "venueKey": "d33ee240-dc59-11e8-a29f-0242ac130002" # LE GRAND REX PARIS
    },
    {
        "eventKey": "d33ee240-dc59-11e8-a29f-0242ac130001", # Concert de Gael Faye
        "isActive": True,
        "key": "d33ee240-dc59-11e8-a29f-0242ac130002",
        "venueKey": "d33ee240-dc59-11e8-a29f-0242ac130004" # THEATRE DE L ODEON
    },
    {
        "eventKey": "d33ee240-dc59-11e8-a29f-0242ac130002", # PNL chante Marx
        "isActive": True,
        "key": "d33ee240-dc59-11e8-a29f-0242ac130003",
        "venueKey": "d33ee240-dc59-11e8-a29f-0242ac130004" # THEATRE DE L ODEON
    },
    {
        "isActive": True,
        "key": "d33ee240-dc59-11e8-a29f-0242ac130004",
        "thingKey": "d33ee240-dc59-11e8-a29f-0242ac130000", # Ravage,
        "venueKey": "d33ee240-dc59-11e8-a29f-0242ac130004" # THEATRE DE L ODEON
    },
    {
        "isActive": True,
        "key": "d33ee240-dc59-11e8-a29f-0242ac130005",
        "thingKey": "d33ee240-dc59-11e8-a29f-0242ac130001", # Le Monde Diplomatique
        "venueKey": "d33ee240-dc59-11e8-a29f-0242ac130005" # THEATRE DE L ODEON (OL)
    }
]
OFFER_MOCKS += SCRATCH_OFFER_MOCKS
