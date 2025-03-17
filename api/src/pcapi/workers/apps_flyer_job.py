from pcapi.connectors.apps_flyer import log_offer_event
from pcapi.connectors.apps_flyer import log_user_event
from pcapi.core.bookings.models import Booking
from pcapi.core.offers.models import Stock
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
    if 15 <= user.age <= 18:
        log_user_event(user, f"af_complete_registration_{user.age}")
    elif user.age >= 19:
        log_user_event(user, "af_complete_registration_19+")


@job(worker.default_queue)
def log_user_booked_offer_event_job(booking_id: int) -> None:
    booking = Booking.query.get(booking_id).joinedload(Booking.user).joinedload(Booking.stock).joinedload(Stock.offer)
    log_offer_event(booking, "af_complete_book_offer")
