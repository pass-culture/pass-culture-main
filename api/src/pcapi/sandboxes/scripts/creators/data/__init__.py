from pcapi.sandboxes.scripts.creators.data.create_data_admin_users import *
from pcapi.sandboxes.scripts.creators.data.create_data_app_users import *
from pcapi.sandboxes.scripts.creators.data.create_data_bookings import *
from pcapi.sandboxes.scripts.creators.data.create_data_criterion import (
    associate_criterion_to_one_offer_with_mediation,
)
from pcapi.sandboxes.scripts.creators.data.create_data_criterion import create_data_criteria

from pcapi.sandboxes.scripts.creators.data.create_data_event_occurrences import *
from pcapi.sandboxes.scripts.creators.data.create_data_event_offers import *
from pcapi.sandboxes.scripts.creators.data.create_data_event_products import *
from pcapi.sandboxes.scripts.creators.data.create_data_event_stocks import *
from pcapi.sandboxes.scripts.creators.data.create_data_mediations import *
from pcapi.sandboxes.scripts.creators.data.create_data_offerers_with_pro_users import *

from pcapi.sandboxes.scripts.creators.data.create_data_pro_users import *
from pcapi.sandboxes.scripts.creators.data.create_data_pro_users_api_keys import *

from pcapi.sandboxes.scripts.creators.data.create_data_thing_offers import *
from pcapi.sandboxes.scripts.creators.data.create_data_thing_products import *
from pcapi.sandboxes.scripts.creators.data.create_data_thing_stocks import *
from pcapi.sandboxes.scripts.creators.data.create_data_venue_types import *
from pcapi.sandboxes.scripts.creators.data.create_data_venues import *

from pcapi.sandboxes.scripts.creators.data.create_offers_with_status import create_offers_with_specific_status
from pcapi.scripts.venue.venue_label.create_venue_labels import create_venue_labels


def save_data_sandbox() -> None:
    venue_types = create_data_venue_types()
    (offerers_by_name_data, pro_users_by_name_data) = create_data_offerers_with_pro_users()

    admin_users_by_name = create_data_admin_users()
    pro_users_by_name_data = create_data_pro_users(offerers_by_name_data)
    
    app_users_by_name_data =create_data_app_users_data()
    users_by_name_data=  dict(dict(admin_users_by_name, **pro_users_by_name_data), **app_users_by_name_data)
    
    venues_by_name_data = create_data_venues_data(offerers_by_name_data, venue_types)
    
    event_products_by_name_data = create_data_event_products()
    thing_products_by_name_data = create_data_thing_products()

    event_offers_by_name_data = create_data_event_offers(event_products_by_name_data, offerers_by_name_data)
    thing_offers_by_name_data = create_data_thing_offers(thing_products_by_name_data, offerers_by_name_data, venues_by_name_data)

    offers_by_name_data = dict(event_offers_by_name_data, **thing_offers_by_name_data)
    event_occurrences_by_name_data = create_data_event_occurrences(event_offers_by_name_data)

    create_data_event_stocks(event_occurrences_by_name_data)
    create_data_thing_stocks(thing_offers_by_name_data)

    prepare_mediations_folders()
    create_data_mediations(offers_by_name_data)

    criteria_by_name = create_data_criteria()

    associate_criterion_to_one_offer_with_mediation(offers_by_name_data, criteria_by_name)

    create_data_bookings(offers_by_name_data, users_by_name_data)

    create_venue_labels(sandbox=True)

    create_data_pro_users_api_keys(offerers_by_name_data)

    create_offers_with_specific_status()
