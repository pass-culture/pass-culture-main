from flask import render_template

from .. import blueprint
from .. import utils
from pcapi.core.bookings import models as bookings_models
from pcapi.repository import repository



@blueprint.backoffice_v3_web.route("/demo/component/<int:booking_id>/use", methods=["GET"])
def demo_use_booking(booking_id: int) -> utils.BackofficeResponse:
    booking = bookings_models.Booking.query.get(booking_id)

    booking.status = bookings_models.BookingStatus.USED
    repository.save(booking)

    return render_template(
        "demo_component/component.html",
        booking = booking
    )


@blueprint.backoffice_v3_web.route("/demo/component/<int:booking_id>/cancel", methods=["GET"])
def demo_cancel_booking(booking_id: int) -> utils.BackofficeResponse:
    booking = bookings_models.Booking.query.get(booking_id)

    booking.status = bookings_models.BookingStatus.CANCELLED
    repository.save(booking)

    return render_template(
        "demo_component/component.html",
        booking = booking
    )
