from sandboxes.scripts.creators.industrial.create_industrial_events import *
from sandboxes.scripts.creators.industrial.create_industrial_event_occurrences import *
from sandboxes.scripts.creators.industrial.create_industrial_event_offers import *
from sandboxes.scripts.creators.industrial.create_industrial_event_stocks import *
from sandboxes.scripts.creators.industrial.create_industrial_mediations import *
from sandboxes.scripts.creators.industrial.create_industrial_thing_offers import *
from sandboxes.scripts.creators.industrial.create_industrial_thing_stocks import *
from sandboxes.scripts.creators.industrial.create_industrial_things import *
from sandboxes.scripts.creators.industrial.create_industrial_offerers import *
from sandboxes.scripts.creators.industrial.create_industrial_venues import *

def save_industrial_sandbox():
    offerers_by_name = create_industrial_offerers()

    venues_by_name = create_industrial_venues(offerers_by_name)

    events_by_name = create_industrial_events()

    things_by_name = create_industrial_things()

    event_offers_by_name = create_industrial_event_offers(
        events_by_name,
        venues_by_name,
        offerers_by_name
    )

    thing_offers_by_name = create_industrial_thing_offers(
        things_by_name,
        venues_by_name,
        offerers_by_name
    )

    offers_by_name = dict(
        event_offers_by_name,
        **thing_offers_by_name
    )

    event_occurrences_by_name = create_industrial_event_occurrences(event_offers_by_name)

    create_industrial_event_stocks(event_occurrences_by_name)

    create_industrial_thing_stocks(thing_offers_by_name)

    create_industrial_mediations(offers_by_name)
