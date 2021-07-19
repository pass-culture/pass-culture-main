import logging

from sqlalchemy.orm import joinedload

from pcapi.core.bookings.models import Booking
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.educational.models import EducationalBooking
from pcapi.core.educational.models import EducationalBookingStatus
from pcapi.core.educational.models import EducationalInstitution
from pcapi.core.educational.models import EducationalYear
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Stock
from pcapi.core.users.models import User
from pcapi.routes.adage.security import adage_api_key_required
from pcapi.routes.adage.v1.educational_institution import educational_institution_path
from pcapi.routes.adage.v1.serialization.prebooking import GetPreBookingsRequest
from pcapi.routes.adage.v1.serialization.prebooking import PreBookingResponse
from pcapi.routes.adage.v1.serialization.prebooking import PreBookingsResponse
from pcapi.routes.adage.v1.serialization.prebooking import get_pre_bookings_response
from pcapi.serialization.decorator import spectree_serialize


logger = logging.getLogger(__name__)

from . import blueprint


@blueprint.adage_v1.route(educational_institution_path + "/prebookings", methods=["GET"])
@spectree_serialize(api=blueprint.api, response_model=PreBookingsResponse, tags=("get prebookings",))
@adage_api_key_required
def get_pre_bookings(query: GetPreBookingsRequest, year_id: str, uai_code: str) -> PreBookingsResponse:
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

    return get_pre_bookings_response(bookings)


@blueprint.adage_v1.route("/prebookings/<int:pre_booking_id>/confirm", methods=["POST"])
@spectree_serialize(
    api=blueprint.api, response_model=PreBookingResponse, on_error_statuses=[404, 422], tags=("change prebookings",)
)
@adage_api_key_required
def confirm_pre_booking() -> PreBookingResponse:
    """Confirm a prebooking

    Can only work if the prebooking is not confirmed yet."""


@blueprint.adage_v1.route("/prebookings/<int:pre_booking_id>/refuse", methods=["POST"])
@spectree_serialize(
    api=blueprint.api,
    response_model=PreBookingResponse,
    on_error_statuses=[404, 422],
    tags=("change prebookings", "change bookings"),
)
@adage_api_key_required
def refuse_pre_booking() -> PreBookingResponse:
    """Refuse a prebooking confirmation

    Can only work if prebooking is confirmed or pending,
    is not yet used and still refusable."""


@blueprint.adage_v1.route("/prebookings/<int:pre_booking_id>/mark_as_used", methods=["POST"])
@spectree_serialize(
    api=blueprint.api, response_model=PreBookingResponse, on_error_statuses=[404, 422], tags=("change bookings",)
)
@adage_api_key_required
def mark_booking_as_used() -> PreBookingResponse:
    """Mark a booking used by the educational institute

    Can only work if booking is in CONFIRMED status"""
