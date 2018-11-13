from sandboxes.scripts.creators.handmade.create_handmade_bookings import *
from sandboxes.scripts.creators.handmade.create_handmade_deposits import *
from sandboxes.scripts.creators.handmade.create_handmade_event_occurrences import *
from sandboxes.scripts.creators.handmade.create_handmade_event_offers import *
from sandboxes.scripts.creators.handmade.create_handmade_event_stocks import *
from sandboxes.scripts.creators.handmade.create_handmade_events import *
from sandboxes.scripts.creators.handmade.create_handmade_mediations import *
from sandboxes.scripts.creators.handmade.create_handmade_recommendations import *
from sandboxes.scripts.creators.handmade.create_handmade_thing_offers import *
from sandboxes.scripts.creators.handmade.create_handmade_thing_stocks import *
from sandboxes.scripts.creators.handmade.create_handmade_things import *
from sandboxes.scripts.creators.handmade.create_handmade_offerers import *
from sandboxes.scripts.creators.handmade.create_handmade_user_offerers import *
from sandboxes.scripts.creators.handmade.create_handmade_users import *
from sandboxes.scripts.creators.handmade.create_handmade_venues import *

def save_handmade_sandbox():
    offerers_by_name = create_handmade_offerers()

    users_by_name = create_handmade_users()

    create_handmade_deposits(users_by_name)

    create_handmade_user_offerers(users_by_name, offerers_by_name)

    venues_by_name = create_handmade_venues(offerers_by_name)

    events_by_name = create_handmade_events()

    things_by_name = create_handmade_things()

    event_offers_by_name = create_handmade_event_offers(
        events_by_name,
        venues_by_name
    )

    thing_offers_by_name = create_handmade_thing_offers(
        things_by_name,
        venues_by_name
    )

    offers_by_name = dict(
        event_offers_by_name,
        **thing_offers_by_name
    )

    event_occurrences_by_name = create_handmade_event_occurrences(
        event_offers_by_name
    )

    event_stocks = create_handmade_event_stocks(
        event_occurrences_by_name
    )

    thing_stocks = create_handmade_thing_stocks(
        thing_offers_by_name
    )

    stocks_by_name = dict(
        event_stocks,
        **thing_stocks
    )

    mediations_by_name = create_handmade_mediations(
        offers_by_name
    )

    recommendations_by_name = create_handmade_recommendations(
        mediations_by_name,
        offers_by_name,
        users_by_name
    )

    create_handmade_bookings(
        recommendations_by_name,
        stocks_by_name,
        users_by_name
    )
