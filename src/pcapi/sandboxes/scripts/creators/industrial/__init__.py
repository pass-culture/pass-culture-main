from pcapi.sandboxes.scripts.creators.industrial.create_industrial_activation_offers import (
    create_industrial_activation_offers,
)
from pcapi.sandboxes.scripts.creators.industrial.create_industrial_admin_users import *
from pcapi.sandboxes.scripts.creators.industrial.create_industrial_bookings import *
from pcapi.sandboxes.scripts.creators.industrial.create_industrial_criterion import (
    associate_criterion_to_one_offer_with_mediation,
)
from pcapi.sandboxes.scripts.creators.industrial.create_industrial_criterion import create_industrial_criteria
from pcapi.sandboxes.scripts.creators.industrial.create_industrial_educational_bookings import (
    create_industrial_educational_bookings,
)
from pcapi.sandboxes.scripts.creators.industrial.create_industrial_event_occurrences import *
from pcapi.sandboxes.scripts.creators.industrial.create_industrial_event_offers import *
from pcapi.sandboxes.scripts.creators.industrial.create_industrial_event_products import *
from pcapi.sandboxes.scripts.creators.industrial.create_industrial_event_stocks import *
from pcapi.sandboxes.scripts.creators.industrial.create_industrial_mediations import *
from pcapi.sandboxes.scripts.creators.industrial.create_industrial_offer_validation_config import *
from pcapi.sandboxes.scripts.creators.industrial.create_industrial_offerers_with_pro_users import *
from pcapi.sandboxes.scripts.creators.industrial.create_industrial_offers_with_activation_codes import (
    create_industrial_offers_with_activation_codes,
)
from pcapi.sandboxes.scripts.creators.industrial.create_industrial_payments import *
from pcapi.sandboxes.scripts.creators.industrial.create_industrial_pro_users import *
from pcapi.sandboxes.scripts.creators.industrial.create_industrial_pro_users_api_keys import *
from pcapi.sandboxes.scripts.creators.industrial.create_industrial_search_objects import (
    create_industrial_search_indexed_objects,
)
from pcapi.sandboxes.scripts.creators.industrial.create_industrial_thing_offers import *
from pcapi.sandboxes.scripts.creators.industrial.create_industrial_thing_products import *
from pcapi.sandboxes.scripts.creators.industrial.create_industrial_thing_stocks import *
from pcapi.sandboxes.scripts.creators.industrial.create_industrial_venue_types import *
from pcapi.sandboxes.scripts.creators.industrial.create_industrial_venues import *
from pcapi.sandboxes.scripts.creators.industrial.create_industrial_webapp_users import *
from pcapi.scripts.venue.venue_label.create_venue_labels import create_venue_labels


def save_industrial_sandbox() -> None:
    (offerers_by_name, pro_users_by_name) = create_industrial_offerers_with_pro_users()

    admin_users_by_name = create_industrial_admin_users()
    pro_users_by_name = create_industrial_pro_users(offerers_by_name)
    webapp_users_by_name = create_industrial_webapp_users()

    users_by_name = dict(dict(admin_users_by_name, **pro_users_by_name), **webapp_users_by_name)

    venue_types = create_industrial_venue_types()

    venues_by_name = create_industrial_venues(offerers_by_name, venue_types)

    event_products_by_name = create_industrial_event_products()

    thing_products_by_name = create_industrial_thing_products()

    event_offers_by_name = create_industrial_event_offers(event_products_by_name, offerers_by_name)

    thing_offers_by_name = create_industrial_thing_offers(thing_products_by_name, offerers_by_name, venues_by_name)

    create_industrial_offers_with_activation_codes()

    offers_by_name = dict(event_offers_by_name, **thing_offers_by_name)

    event_occurrences_by_name = create_industrial_event_occurrences(event_offers_by_name)

    create_industrial_event_stocks(event_occurrences_by_name)

    create_industrial_thing_stocks(thing_offers_by_name)

    prepare_mediations_folders()
    create_industrial_mediations(offers_by_name)

    criteria_by_name = create_industrial_criteria()

    associate_criterion_to_one_offer_with_mediation(offers_by_name, criteria_by_name)

    create_industrial_bookings(offers_by_name, users_by_name)

    create_industrial_educational_bookings()

    # Now that they booked, we can expire these users' deposit.
    for name, user in users_by_name.items():
        if "has-booked-some-but-deposit-expired" in name:
            user.deposit.expirationDate = datetime.now()
            repository.save(user.deposit)

    create_industrial_payments()

    create_industrial_pro_users_api_keys(offerers_by_name)

    create_industrial_activation_offers()

    create_industrial_search_indexed_objects()

    create_venue_labels()

    create_industrial_offer_validation_config()
