from pcapi.sandboxes.scripts.creators.data.create_industrial_admin_users import *
from pcapi.sandboxes.scripts.creators.data.create_industrial_app_users import *
from pcapi.sandboxes.scripts.creators.data.create_industrial_bookings import *
from pcapi.sandboxes.scripts.creators.data.create_industrial_criterion import (
    associate_criterion_to_one_offer_with_mediation,
)
from pcapi.sandboxes.scripts.creators.data.create_industrial_criterion import create_industrial_criteria

from pcapi.sandboxes.scripts.creators.data.create_industrial_event_occurrences import *
from pcapi.sandboxes.scripts.creators.data.create_industrial_event_offers import *
from pcapi.sandboxes.scripts.creators.data.create_industrial_event_products import *
from pcapi.sandboxes.scripts.creators.data.create_industrial_event_stocks import *
from pcapi.sandboxes.scripts.creators.data.create_industrial_mediations import *
from pcapi.sandboxes.scripts.creators.data.create_industrial_offerers_with_pro_users import *

from pcapi.sandboxes.scripts.creators.data.create_industrial_pro_users import *
from pcapi.sandboxes.scripts.creators.data.create_industrial_pro_users_api_keys import *

from pcapi.sandboxes.scripts.creators.data.create_industrial_thing_offers import *
from pcapi.sandboxes.scripts.creators.data.create_industrial_thing_products import *
from pcapi.sandboxes.scripts.creators.data.create_industrial_thing_stocks import *
from pcapi.sandboxes.scripts.creators.data.create_industrial_venue_types import *
from pcapi.sandboxes.scripts.creators.data.create_industrial_venues import *

from pcapi.sandboxes.scripts.creators.data.create_offers_with_status import create_offers_with_specific_status
from pcapi.scripts.venue.venue_label.create_venue_labels import create_venue_labels


def save_data_sandbox() -> None:
    venue_types = create_industrial_venue_types()
    (offerers_by_name_data, pro_users_by_name_data) = create_industrial_offerers_with_pro_users()

    admin_users_by_name = create_industrial_admin_users()
    pro_users_by_name_data = create_industrial_pro_users(offerers_by_name_data)
    
    app_users_by_name_data =create_industrial_app_users_data()
    users_by_name_data=  dict(dict(admin_users_by_name, **pro_users_by_name_data), **app_users_by_name_data)
    
    venues_by_name_data = create_industrial_venues_data(offerers_by_name_data, venue_types)
    
    event_products_by_name_data = create_industrial_event_products()
    thing_products_by_name_data = create_industrial_thing_products()

    event_offers_by_name_data = create_industrial_event_offers(event_products_by_name_data, offerers_by_name_data)
    thing_offers_by_name_data = create_industrial_thing_offers(thing_products_by_name_data, offerers_by_name_data, venues_by_name_data)

    offers_by_name_data = dict(event_offers_by_name_data, **thing_offers_by_name_data)
    event_occurrences_by_name_data = create_industrial_event_occurrences(event_offers_by_name_data)

    create_industrial_event_stocks(event_occurrences_by_name_data)
    create_industrial_thing_stocks(thing_offers_by_name_data)

    prepare_mediations_folders()
    create_industrial_mediations(offers_by_name_data)

    criteria_by_name = create_industrial_criteria()

    associate_criterion_to_one_offer_with_mediation(offers_by_name_data, criteria_by_name)

    create_industrial_bookings(offers_by_name_data, users_by_name_data)

    create_venue_labels(sandbox=True)

    create_industrial_pro_users_api_keys(offerers_by_name_data)

    create_offers_with_specific_status()
