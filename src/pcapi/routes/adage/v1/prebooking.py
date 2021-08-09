import logging

from pcapi.core.educational import api
from pcapi.core.educational import exceptions
from pcapi.core.educational.repository import find_educational_bookings_for_adage
from pcapi.models.api_errors import ApiErrors
from pcapi.routes.adage.security import adage_api_key_required
from pcapi.routes.adage.v1.educational_institution import educational_institution_path
from pcapi.routes.adage.v1.serialization.prebooking import EducationalBookingResponse
from pcapi.routes.adage.v1.serialization.prebooking import EducationalBookingsResponse
from pcapi.routes.adage.v1.serialization.prebooking import GetEducationalBookingsRequest
from pcapi.routes.adage.v1.serialization.prebooking import serialize_educational_booking
from pcapi.routes.adage.v1.serialization.prebooking import serialize_educational_bookings
from pcapi.serialization.decorator import spectree_serialize


logger = logging.getLogger(__name__)

from . import blueprint


@blueprint.adage_v1.route(educational_institution_path + "/prebookings", methods=["GET"])
@spectree_serialize(api=blueprint.api, response_model=EducationalBookingsResponse, tags=("get prebookings",))
@adage_api_key_required
def get_educational_bookings(
    query: GetEducationalBookingsRequest, year_id: str, uai_code: str
) -> EducationalBookingsResponse:
    bookings_base_query = (
        Booking.query.join(EducationalBooking, Booking.educationalBookingId == EducationalBooking.id)
        .join(EducationalInstitution)
        .join(EducationalYear)
        .options(joinedload(Booking.user, innerjoin=True))
        .options(
            joinedload(Booking.stock, innerjoin=True)
            .joinedload(Stock.offer, innerjoin=True)
            .joinedload(Offer.venue, innerjoin=True)
        )
        .options(
            joinedload(Booking.educationalBooking).joinedload(EducationalBooking.educationalInstitution, innerjoin=True)
        )
        .filter(EducationalInstitution.institutionId == uai_code)
        .filter(EducationalYear.adageId == year_id)
    )

    if query.redactorEmail is not None:
        bookings_base_query = bookings_base_query.join(User).filter(User.email == query.redactorEmail)

    if query.status is not None:
        if query.status in BookingStatus:
            bookings_base_query = bookings_base_query.filter(Booking.status == query.status)

        if query.status in EducationalBookingStatus:
            bookings_base_query = bookings_base_query.filter(EducationalBooking.status == query.status)

    bookings = bookings_base_query.all()

    return EducationalBookingsResponse(
        prebookings=serialize_educational_bookings([booking.educationalBooking for booking in bookings])
    )


@blueprint.adage_v1.route("/prebookings/<int:educational_booking_id>/confirm", methods=["POST"])
@spectree_serialize(
    api=blueprint.api,
    response_model=EducationalBookingResponse,
    on_error_statuses=[404, 422],
    tags=("change prebookings",),
)
@adage_api_key_required
def confirm_prebooking(educational_booking_id: int) -> EducationalBookingResponse:
    try:
        educational_booking = api.confirm_educational_booking(educational_booking_id)
    except exceptions.InsufficientFund:
        raise ApiErrors({"deposit": "Fond insuffisant pour confirmer cette réservation"}, status_code=422)
    except exceptions.InsufficientTemporaryFund:
        raise ApiErrors({"deposit": "Montant du fond définitif en attente de validation"}, status_code=422)
    except exceptions.EducationalBookingNotFound:
        raise ApiErrors({"id": "Aucune réservation n'a été trouvée avec cet identifiant"}, status_code=404)
    except exceptions.EducationalDepositNotFound:
        raise ApiErrors({"deposit": "Aucun budget n'a été trouvé pour valider cette réservation"}, status_code=404)

    return serialize_educational_booking(educational_booking)


@blueprint.adage_v1.route("/prebookings/<int:educational_booking_id>/refuse", methods=["POST"])
@spectree_serialize(
    api=blueprint.api,
    response_model=EducationalBookingResponse,
    on_error_statuses=[404, 422],
    tags=("change prebookings", "change bookings"),
)
@adage_api_key_required
def refuse_pre_booking() -> EducationalBookingResponse:
    """Refuse a prebooking confirmation

    Can only work if prebooking is confirmed or pending,
    is not yet used and still refusable."""


@blueprint.adage_v1.route("/prebookings/<int:educational_booking_id>/mark_as_used", methods=["POST"])
@spectree_serialize(
    api=blueprint.api,
    response_model=EducationalBookingResponse,
    on_error_statuses=[404, 422],
    tags=("change bookings",),
)
@adage_api_key_required
def mark_booking_as_used() -> EducationalBookingResponse:
    """Mark a booking used by the educational institute

    Can only work if booking is in CONFIRMED status"""
