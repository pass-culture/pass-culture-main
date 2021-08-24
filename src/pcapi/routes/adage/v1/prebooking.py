import logging

from pcapi.core.educational import api
from pcapi.core.educational import exceptions
from pcapi.core.educational.repository import find_educational_bookings_for_adage
from pcapi.models.api_errors import ApiErrors
from pcapi.routes.adage.security import adage_api_key_required
from pcapi.routes.adage.v1.educational_institution import educational_institution_path
from pcapi.routes.adage.v1.serialization import constants
from pcapi.routes.adage.v1.serialization import prebooking as prebooking_serialization
from pcapi.serialization.decorator import spectree_serialize


logger = logging.getLogger(__name__)

from . import blueprint


@blueprint.adage_v1.route(educational_institution_path + "/prebookings", methods=["GET"])
@spectree_serialize(
    api=blueprint.api, response_model=prebooking_serialization.EducationalBookingsResponse, tags=("get prebookings",)
)
@adage_api_key_required
def get_educational_bookings(
    query: prebooking_serialization.GetEducationalBookingsRequest, year_id: str, uai_code: str
) -> prebooking_serialization.EducationalBookingsResponse:
    educational_bookings = find_educational_bookings_for_adage(
        uai_code=uai_code,
        year_id=year_id,
        redactor_email=query.redactorEmail,
        status=query.status,
    )

    return prebooking_serialization.EducationalBookingsResponse(
        prebookings=prebooking_serialization.serialize_educational_bookings(educational_bookings)
    )


@blueprint.adage_v1.route("/prebookings/<int:educational_booking_id>/confirm", methods=["POST"])
@spectree_serialize(
    api=blueprint.api,
    response_model=prebooking_serialization.EducationalBookingResponse,
    on_error_statuses=[404, 422],
    tags=("change prebookings",),
)
@adage_api_key_required
def confirm_prebooking(educational_booking_id: int) -> prebooking_serialization.EducationalBookingResponse:
    try:
        educational_booking = api.confirm_educational_booking(educational_booking_id)
    except exceptions.InsufficientFund:
        raise ApiErrors({"code": "INSUFFICIENT_FUND"}, status_code=422)
    except exceptions.InsufficientTemporaryFund:
        raise ApiErrors({"code": "INSUFFICIENT_FUND_DEPOSIT_NOT_FINAL"}, status_code=422)
    except exceptions.EducationalBookingIsRefused:
        raise ApiErrors({"code": "EDUCATIONAL_BOOKING_IS_REFUSED"}, status_code=422)
    except exceptions.BookingIsCancelled:
        raise ApiErrors({"code": "EDUCATIONAL_BOOKING_IS_CANCELLED"}, status_code=422)
    except exceptions.EducationalBookingNotFound:
        raise ApiErrors({"code": constants.EDUCATIONAL_BOOKING_NOT_FOUND}, status_code=404)
    except exceptions.EducationalDepositNotFound:
        raise ApiErrors({"code": "DEPOSIT_NOT_FOUND"}, status_code=404)

    return prebooking_serialization.serialize_educational_booking(educational_booking)


@blueprint.adage_v1.route("/prebookings/<int:educational_booking_id>/refuse", methods=["POST"])
@spectree_serialize(
    api=blueprint.api,
    response_model=prebooking_serialization.EducationalBookingResponse,
    on_error_statuses=[404, 422],
    tags=("change prebookings", "change bookings"),
)
@adage_api_key_required
def refuse_pre_booking(educational_booking_id: int) -> prebooking_serialization.EducationalBookingResponse:
    """Refuse a prebooking confirmation

    Can only work if prebooking is confirmed or pending,
    is not yet used and still refusable."""
    try:
        educational_booking = api.refuse_educational_booking(educational_booking_id)
    except exceptions.EducationalBookingNotFound:
        raise ApiErrors({"code": constants.EDUCATIONAL_BOOKING_NOT_FOUND}, status_code=404)
    except exceptions.EducationalBookingNotRefusable:
        raise ApiErrors({"code": "EDUCATIONAL_BOOKING_NOT_REFUSABLE"}, status_code=422)
    except exceptions.EducationalBookingAlreadyCancelled:
        raise ApiErrors({"code": "EDUCATIONAL_BOOKING_ALREADY_CANCELLED"}, status_code=422)

    return prebooking_serialization.serialize_educational_booking(educational_booking)


@blueprint.adage_v1.route("/prebookings/<int:educational_booking_id>/mark_as_used", methods=["POST"])
@spectree_serialize(
    api=blueprint.api,
    response_model=prebooking_serialization.EducationalBookingResponse,
    on_error_statuses=[404, 422],
    tags=("change bookings",),
)
@adage_api_key_required
def mark_booking_as_used(educational_booking_id: int) -> prebooking_serialization.EducationalBookingResponse:
    """Mark a booking used by the educational institute

    Can only work if booking is in CONFIRMED status"""
    try:
        educational_booking = api.mark_educational_booking_as_used_by_institute(educational_booking_id)
    except exceptions.EducationalBookingNotFound:
        raise ApiErrors({"code": constants.EDUCATIONAL_BOOKING_NOT_FOUND}, status_code=404)
    except exceptions.EducationalBookingNotConfirmedYet:
        raise ApiErrors({"code": "EDUCATIONAL_BOOKING_NOT_CONFIRMED_YET"}, status_code=422)

    return prebooking_serialization.serialize_educational_booking(educational_booking)
