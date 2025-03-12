from pcapi.connectors.apps_flyer import log_offer_event
from pcapi.connectors.apps_flyer import log_user_event
from pcapi.core.bookings.models import Booking
from pcapi.core.offers.models import Offer
from pcapi.core.users.models import User
from pcapi.workers import worker
from pcapi.workers.decorators import job


@job(worker.default_queue)
def log_user_becomes_beneficiary_event_job(user_id: int) -> None:
    user = User.query.get(user_id)
    log_user_event(user, "af_complete_beneficiary")

    if 15 <= user.age <= 17:
        log_user_event(user, "af_complete_beneficiary_underage")
        log_user_event(user, f"af_complete_beneficiary_{user.age}")
    elif user.age >= 18:
        log_user_event(user, "af_complete_beneficiary_18")


@job(worker.default_queue)
def log_user_registration_event_job(user_id: int) -> None:
    user = User.query.get(user_id)
    if user.age == 15:
        log_user_event(user, "af_complete_registration_15")
    elif user.age == 16:
        log_user_event(user, "af_complete_registration_16")
    elif user.age == 17:
        log_user_event(user, "af_complete_registration_17")
    elif user.age == 18:
        log_user_event(user, "af_complete_registration_18")
    elif user.age >= 19:
        log_user_event(user, "af_complete_registration_19+")


@job(worker.default_queue)
def log_user_booked_offer_event_job(user_id: int, offer_id: int, booking_id: int) -> None:
    user = User.query.get(user_id)
    offer = Offer.query.get(offer_id)
    booking = Booking.query.get(booking_id)

    log_offer_event(offer, booking, user, "af_complete_book_offer")
