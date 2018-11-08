""" save sandbox """
from models import Booking,\
                   Deposit,\
                   EventOccurrence,\
                   Event,\
                   Mediation,\
                   Offerer,\
                   Offer,\
                   Recommendation,\
                   Stock,\
                   Thing,\
                   UserOfferer,\
                   User,\
                   Venue
from models.auto_increment import make_auto_increment_id_clamped_to_last_inserted_object
from sandboxes.scripts.utils.creators import create_or_find_objects
from sandboxes import scripts

def save_sandbox(name):

    make_auto_increment_id_clamped_to_last_inserted_object()

    script_name = "sandbox_" + name
    sandbox_module = getattr(scripts, script_name)
    create_or_find_objects(
        Offerer,
        *sandbox_module.OFFERER_MOCKS
    )
    create_or_find_objects(
        User,
        *sandbox_module.USER_MOCKS
    )
    create_or_find_objects(
        UserOfferer,
        *sandbox_module.USER_OFFERER_MOCKS
    )
    create_or_find_objects(
        Venue,
        *sandbox_module.VENUE_MOCKS
    )
    create_or_find_objects(
        Event,
        *sandbox_module.EVENT_MOCKS
    )
    create_or_find_objects(
        Thing,
        *sandbox_module.THING_MOCKS
    )
    create_or_find_objects(
        Offer,
        *sandbox_module.OFFER_MOCKS
    )
    create_or_find_objects(
        EventOccurrence,
        *sandbox_module.EVENT_OCCURRENCE_MOCKS
    )
    create_or_find_objects(
        Stock,
        *sandbox_module.STOCK_MOCKS
    )
    create_or_find_objects(
        Deposit,
        *sandbox_module.DEPOSIT_MOCKS
    )
    create_or_find_objects(
        Mediation,
        *sandbox_module.MEDIATION_MOCKS
    )
    create_or_find_objects(
        Recommendation,
        *sandbox_module.RECOMMENDATION_MOCKS
    )
    create_or_find_objects(
        Booking,
        *sandbox_module.BOOKING_MOCKS
    )
