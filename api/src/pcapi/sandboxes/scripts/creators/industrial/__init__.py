from datetime import datetime

from pcapi.repository import repository
from pcapi.sandboxes.scripts.creators.industrial.add_accessibility_compliance_to_venues import (
    add_accessibility_compliance_to_venues,
)
from pcapi.sandboxes.scripts.creators.industrial.create_closed_offerers import create_closed_offerers
from pcapi.sandboxes.scripts.creators.industrial.create_event_with_opening_hours_offers import (
    create_offerer_with_event_with_opening_hours,
)
from pcapi.sandboxes.scripts.creators.industrial.create_future_offers import create_future_offers
from pcapi.sandboxes.scripts.creators.industrial.create_gdpr_user_extracts import create_gdpr_user_extract_data
from pcapi.sandboxes.scripts.creators.industrial.create_industrial_admin_users import create_industrial_admin_users
from pcapi.sandboxes.scripts.creators.industrial.create_industrial_app_users import create_industrial_app_users
from pcapi.sandboxes.scripts.creators.industrial.create_industrial_bank_accounts import create_industrial_bank_accounts
from pcapi.sandboxes.scripts.creators.industrial.create_industrial_bookings import create_fraudulent_bookings
from pcapi.sandboxes.scripts.creators.industrial.create_industrial_bookings import create_industrial_bookings
from pcapi.sandboxes.scripts.creators.industrial.create_industrial_bookings_for_statistics import (
    create_industrial_bookings_for_statistics,
)
from pcapi.sandboxes.scripts.creators.industrial.create_industrial_chronicles import create_industrial_chronicles
from pcapi.sandboxes.scripts.creators.industrial.create_industrial_commercial_gestures import (
    create_industrial_commercial_gestures,
)
from pcapi.sandboxes.scripts.creators.industrial.create_industrial_complex_offers import create_complex_offers
from pcapi.sandboxes.scripts.creators.industrial.create_industrial_criterion import (
    associate_criterion_to_one_offer_with_mediation,
)
from pcapi.sandboxes.scripts.creators.industrial.create_industrial_criterion import create_industrial_criteria
from pcapi.sandboxes.scripts.creators.industrial.create_industrial_draft_offers import create_industrial_draft_offers
from pcapi.sandboxes.scripts.creators.industrial.create_industrial_eac_data import create_eac_data
from pcapi.sandboxes.scripts.creators.industrial.create_industrial_event_occurrences import (
    create_industrial_event_occurrences,
)
from pcapi.sandboxes.scripts.creators.industrial.create_industrial_event_offers import create_industrial_event_offers
from pcapi.sandboxes.scripts.creators.industrial.create_industrial_event_stocks import create_industrial_event_stocks
from pcapi.sandboxes.scripts.creators.industrial.create_industrial_headline_offers import (
    create_industrial_headline_offers,
)
from pcapi.sandboxes.scripts.creators.industrial.create_industrial_incidents import create_industrial_incidents
from pcapi.sandboxes.scripts.creators.industrial.create_industrial_individual_offerers import (
    create_industrial_individual_offerers,
)
from pcapi.sandboxes.scripts.creators.industrial.create_industrial_invoices import build_many_extra_invoices
from pcapi.sandboxes.scripts.creators.industrial.create_industrial_invoices import create_industrial_invoices
from pcapi.sandboxes.scripts.creators.industrial.create_industrial_iris import create_iris
from pcapi.sandboxes.scripts.creators.industrial.create_industrial_mediations import create_industrial_mediations
from pcapi.sandboxes.scripts.creators.industrial.create_industrial_offer_price_limitation_rules import (
    create_industrial_offer_price_limitation_rules,
)
from pcapi.sandboxes.scripts.creators.industrial.create_industrial_offer_validation_rules import (
    create_industrial_offer_validation_rules,
)
from pcapi.sandboxes.scripts.creators.industrial.create_industrial_offerer_addresses import (
    create_industrial_offerer_addresses,
)
from pcapi.sandboxes.scripts.creators.industrial.create_industrial_offerer_confidence_rules import (
    create_industrial_offerer_confidence_rules,
)
from pcapi.sandboxes.scripts.creators.industrial.create_industrial_offerer_tags import create_industrial_offerer_tags
from pcapi.sandboxes.scripts.creators.industrial.create_industrial_offerers import create_industrial_offerers
from pcapi.sandboxes.scripts.creators.industrial.create_industrial_pro_users import create_industrial_pro_users
from pcapi.sandboxes.scripts.creators.industrial.create_industrial_pro_users_api_keys import (
    create_industrial_pro_users_api_keys,
)
from pcapi.sandboxes.scripts.creators.industrial.create_industrial_search_objects import (
    create_industrial_search_indexed_objects,
)
from pcapi.sandboxes.scripts.creators.industrial.create_industrial_thing_offers import create_industrial_thing_offers
from pcapi.sandboxes.scripts.creators.industrial.create_industrial_thing_stocks import create_industrial_thing_stocks
from pcapi.sandboxes.scripts.creators.industrial.create_industrial_venues import create_industrial_venues
from pcapi.sandboxes.scripts.creators.industrial.create_industrial_venues_with_timezone import (
    create_industrial_venues_with_timezone,
)
from pcapi.sandboxes.scripts.creators.industrial.create_new_caledonia_objects import create_new_caledonia_objects
from pcapi.sandboxes.scripts.creators.industrial.create_offer_with_thousand_stocks import (
    create_offer_with_thousand_stocks,
)
from pcapi.sandboxes.scripts.creators.industrial.create_offerer_providers_for_apis import (
    create_offerer_providers_for_apis,
)
from pcapi.sandboxes.scripts.creators.industrial.create_offerer_with_several_venues import (
    create_offerer_with_several_venues,
)
from pcapi.sandboxes.scripts.creators.industrial.create_offerer_with_venue_provider_and_external_bookings import (
    create_industrial_provider_external_bookings,
)
from pcapi.sandboxes.scripts.creators.industrial.create_offers_with_ean import create_offers_with_ean
from pcapi.sandboxes.scripts.creators.industrial.create_offers_with_price_categories import (
    create_offers_with_price_categories,
)
from pcapi.sandboxes.scripts.creators.industrial.create_offers_with_status import create_offers_with_status
from pcapi.sandboxes.scripts.creators.industrial.create_special_events import create_special_events
from pcapi.sandboxes.scripts.creators.industrial.create_user_account_update_requests import (
    create_user_account_update_requests,
)
from pcapi.sandboxes.scripts.creators.industrial.create_user_offerers import create_user_offerers


def save_industrial_sandbox() -> None:
    create_iris()
    offerers_by_name = create_industrial_offerers()

    admin_users_by_name = create_industrial_admin_users()
    pro_users_by_name = create_industrial_pro_users(offerers_by_name)
    app_users_by_name = create_industrial_app_users()

    users_by_name = dict(dict(admin_users_by_name, **pro_users_by_name), **app_users_by_name)

    venues_by_name = create_industrial_venues(offerers_by_name)

    event_offers_by_name = create_industrial_event_offers(offerers_by_name)

    thing_offers_by_name = create_industrial_thing_offers(offerers_by_name, venues_by_name)

    create_industrial_draft_offers(offerers_by_name)

    offers_by_name = dict(event_offers_by_name, **thing_offers_by_name)

    event_occurrences_by_name = create_industrial_event_occurrences(event_offers_by_name)

    create_industrial_event_stocks(event_occurrences_by_name)

    create_industrial_thing_stocks(thing_offers_by_name)

    create_industrial_mediations(offers_by_name)

    create_industrial_headline_offers(offers_by_name)

    criteria_by_name = create_industrial_criteria()

    associate_criterion_to_one_offer_with_mediation(offers_by_name, criteria_by_name)

    create_industrial_bookings(offers_by_name, users_by_name)

    create_complex_offers(offerers_by_name)

    create_eac_data()

    # Now that they booked, we can expire these users' deposit.
    for name, user in users_by_name.items():
        if "has-booked-some-but-deposit-expired" in name:
            assert user.deposit  # helps mypy
            user.deposit.expirationDate = datetime.utcnow()
            repository.save(user.deposit)

    create_industrial_pro_users_api_keys(offerers_by_name)

    create_industrial_search_indexed_objects()

    create_industrial_provider_external_bookings()

    create_industrial_offerer_tags()

    offerer_with_several_venues = create_offerer_with_several_venues()

    create_offers_with_status(offerer_with_several_venues)

    create_offer_with_thousand_stocks(offerer_with_several_venues)

    create_offers_with_price_categories(offerer_with_several_venues)

    create_offerer_providers_for_apis()

    create_offerer_with_event_with_opening_hours()

    create_offers_with_ean()

    create_future_offers()

    create_industrial_incidents()

    create_industrial_individual_offerers()

    create_industrial_bank_accounts()

    create_industrial_offerer_addresses()

    create_industrial_venues_with_timezone()

    add_accessibility_compliance_to_venues()

    create_industrial_offerer_confidence_rules()

    create_new_caledonia_objects()

    create_gdpr_user_extract_data()

    create_industrial_commercial_gestures()

    create_special_events()

    create_industrial_chronicles()

    create_industrial_bookings_for_statistics()

    create_user_account_update_requests()

    create_industrial_invoices()

    create_closed_offerers()

    # should be the last function called to create invoices
    build_many_extra_invoices()

    create_fraudulent_bookings()

    # run this last as we fill out missing user offerers
    create_user_offerers()
