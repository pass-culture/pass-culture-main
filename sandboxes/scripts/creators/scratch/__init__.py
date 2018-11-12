from sandboxes.scripts.creators.scratch.create_scratch_bookings import *
from sandboxes.scripts.creators.scratch.create_scratch_event_occurrences import *
from sandboxes.scripts.creators.scratch.create_scratch_event_offers import *
from sandboxes.scripts.creators.scratch.create_scratch_event_stocks import *
from sandboxes.scripts.creators.scratch.create_scratch_events import *
from sandboxes.scripts.creators.scratch.create_scratch_mediations import *
from sandboxes.scripts.creators.scratch.create_scratch_recommendations import *
from sandboxes.scripts.creators.scratch.create_scratch_thing_offers import *
from sandboxes.scripts.creators.scratch.create_scratch_thing_stocks import *
from sandboxes.scripts.creators.scratch.create_scratch_things import *
from sandboxes.scripts.creators.scratch.create_scratch_offerers import *
from sandboxes.scripts.creators.scratch.create_scratch_user_offerers import *
from sandboxes.scripts.creators.scratch.create_scratch_users import *
from sandboxes.scripts.creators.scratch.create_scratch_venues import *

def save_scratch_sandbox():
    scratch_offerers_by_name = create_scratch_offerers()

    scratch_users_by_name = create_scratch_users()

    create_scratch_user_offerers(scratch_users_by_name, scratch_offerers_by_name)

    scratch_venues_by_name = create_scratch_venues(scratch_offerers_by_name)

    scratch_events_by_name = create_scratch_events()

    scratch_things_by_name = create_scratch_things()

    scratch_event_offers_by_name = create_scratch_event_offers(
        scratch_events_by_name,
        scratch_venues_by_name
    )

    scratch_thing_offers_by_name = create_scratch_thing_offers(
        scratch_things_by_name,
        scratch_venues_by_name
    )

    scratch_offers_by_name = dict(
        scratch_event_offers_by_name,
        **scratch_thing_offers_by_name
    )

    scratch_event_occurrences_by_name = create_scratch_event_occurrences(scratch_event_offers_by_name) 

    scratch_event_stocks = create_scratch_event_stocks(scratch_event_offers_by_name)

    scratch_thing_stocks = create_scratch_thing_stocks(scratch_thing_offers_by_name)

    scratch_stocks_by_name = dict(
        scratch_event_stocks,
        **scratch_thing_stocks
    )

    scratch_mediations_by_name = create_scratch_mediations(scratch_offers_by_name)

    scratch_recommendations_by_name = create_scratch_recommendations(
        scratch_mediations_by_name,
        scratch_offers_by_name,
        scratch_users_by_name
    )

    create_scratch_bookings(
        scratch_recommendations_by_name,
        scratch_stocks_by_name,
        scratch_users_by_name
    )
