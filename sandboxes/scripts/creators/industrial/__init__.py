from sandboxes.scripts.creators.industrial.create_industrial_bookings import *
from sandboxes.scripts.creators.industrial.create_industrial_deposits import *
from sandboxes.scripts.creators.industrial.create_industrial_events import *
from sandboxes.scripts.creators.industrial.create_industrial_event_occurrences import *
from sandboxes.scripts.creators.industrial.create_industrial_event_offers import *
from sandboxes.scripts.creators.industrial.create_industrial_event_stocks import *
from sandboxes.scripts.creators.industrial.create_industrial_mediations import *
from sandboxes.scripts.creators.industrial.create_industrial_recommendations import *
from sandboxes.scripts.creators.industrial.create_industrial_thing_offers import *
from sandboxes.scripts.creators.industrial.create_industrial_thing_stocks import *
from sandboxes.scripts.creators.industrial.create_industrial_things import *
from sandboxes.scripts.creators.industrial.create_industrial_offerers_with_pro_users import *
from sandboxes.scripts.creators.industrial.create_industrial_venues import *
from sandboxes.scripts.creators.industrial.create_industrial_admin_users import *
from sandboxes.scripts.creators.industrial.create_industrial_pro_users import *
from sandboxes.scripts.creators.industrial.create_industrial_webapp_users import *

def save_industrial_sandbox():

    (
        offerers_by_name,
        pro_users_by_name,
        user_offerers_by_name
    ) = create_industrial_offerers_with_pro_users()

    admin_users_by_name = create_industrial_admin_users()
    pro_users_by_name = create_industrial_pro_users()
    webapp_users_by_name = create_industrial_webapp_users()

    users_by_name = dict(
        pro_users_by_name,
        **dict(admin_users_by_name, **webapp_users_by_name)
    )

    create_industrial_deposits(users_by_name)

    venues_by_name = create_industrial_venues(offerers_by_name)

    events_by_name = create_industrial_events()

    things_by_name = create_industrial_things()

    event_offers_by_name = create_industrial_event_offers(
        events_by_name,
        offerers_by_name
    )

    thing_offers_by_name = create_industrial_thing_offers(
        things_by_name,
        offerers_by_name,
        venues_by_name
    )

    offers_by_name = dict(
        event_offers_by_name,
        **thing_offers_by_name
    )

    event_occurrences_by_name = create_industrial_event_occurrences(event_offers_by_name)

    event_stocks_by_name = create_industrial_event_stocks(event_occurrences_by_name)

    thing_stocks_by_name = create_industrial_thing_stocks(thing_offers_by_name)

    stocks_by_name = dict(
        event_stocks_by_name,
        **thing_stocks_by_name
    )

    mediations_by_name = create_industrial_mediations(offers_by_name)

    recommendations_by_name = create_industrial_recommendations(
        mediations_by_name,
        offers_by_name,
        users_by_name
    )

    create_industrial_bookings(recommendations_by_name, stocks_by_name)
