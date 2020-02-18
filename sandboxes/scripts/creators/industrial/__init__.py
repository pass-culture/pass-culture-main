from models import DiscoveryView
from sandboxes.scripts.creators.industrial.create_industrial_activation_offers import \
    create_industrial_activation_offers
from sandboxes.scripts.creators.industrial.create_industrial_admin_users import *
from sandboxes.scripts.creators.industrial.create_industrial_algolia_objects import \
    create_industrial_algolia_indexed_objects
from sandboxes.scripts.creators.industrial.create_industrial_bookings import *
from sandboxes.scripts.creators.industrial.create_industrial_criterion import create_industrial_criteria, \
    associate_criterion_to_one_offer_with_mediation
from sandboxes.scripts.creators.industrial.create_industrial_deposits import *
from sandboxes.scripts.creators.industrial.create_industrial_event_occurrences import *
from sandboxes.scripts.creators.industrial.create_industrial_event_offers import *
from sandboxes.scripts.creators.industrial.create_industrial_event_products import *
from sandboxes.scripts.creators.industrial.create_industrial_event_stocks import *
from sandboxes.scripts.creators.industrial.create_industrial_mediations import *
from sandboxes.scripts.creators.industrial.create_industrial_offerers_with_pro_users import *
from sandboxes.scripts.creators.industrial.create_industrial_payments import *
from sandboxes.scripts.creators.industrial.create_industrial_pro_users import *
from sandboxes.scripts.creators.industrial.create_industrial_pro_users_api_keys import *
from sandboxes.scripts.creators.industrial.create_industrial_recommendations import *
from sandboxes.scripts.creators.industrial.create_industrial_thing_offers import *
from sandboxes.scripts.creators.industrial.create_industrial_thing_products import *
from sandboxes.scripts.creators.industrial.create_industrial_thing_stocks import *
from sandboxes.scripts.creators.industrial.create_industrial_venues import *
from sandboxes.scripts.creators.industrial.create_industrial_webapp_users import *


def save_industrial_sandbox():
    (
        offerers_by_name,
        pro_users_by_name
    ) = create_industrial_offerers_with_pro_users()

    admin_users_by_name = create_industrial_admin_users()
    pro_users_by_name = create_industrial_pro_users()
    webapp_users_by_name = create_industrial_webapp_users()

    users_by_name = dict(dict(admin_users_by_name, **pro_users_by_name), **webapp_users_by_name)

    create_industrial_deposits(users_by_name)

    venues_by_name = create_industrial_venues(offerers_by_name)

    event_products_by_name = create_industrial_event_products()

    thing_products_by_name = create_industrial_thing_products()

    event_offers_by_name = create_industrial_event_offers(
        event_products_by_name,
        offerers_by_name
    )

    thing_offers_by_name = create_industrial_thing_offers(
        thing_products_by_name,
        offerers_by_name,
        venues_by_name
    )

    offers_by_name = dict(
        event_offers_by_name,
        **thing_offers_by_name
    )

    event_occurrences_by_name = create_industrial_event_occurrences(event_offers_by_name)

    create_industrial_event_stocks(event_occurrences_by_name)

    create_industrial_thing_stocks(thing_offers_by_name)

    create_industrial_mediations(offers_by_name)

    # DiscoveryView.refresh()
    recommendations_by_name = create_industrial_recommendations(
        offers_by_name,
        users_by_name
    )

    criteria_by_name = create_industrial_criteria()

    associate_criterion_to_one_offer_with_mediation(offers_by_name, criteria_by_name)

    create_industrial_bookings(recommendations_by_name)

    create_industrial_payments()

    create_industrial_pro_users_api_keys(offerers_by_name)

    create_industrial_activation_offers()

    create_industrial_algolia_indexed_objects()
