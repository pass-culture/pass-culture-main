from typing import Any

from flask import jsonify
from flask_login import login_required
from sqlalchemy.orm import joinedload

from pcapi.core.bookings.models import Booking
from pcapi.routes.apis import private_api
from pcapi.routes.serialization import as_dict
from pcapi.utils.human_ids import dehumanize
from pcapi.utils.includes import WEBAPP_GET_BOOKING_INCLUDES


@private_api.route("/bookings/<booking_id>", methods=["GET"])
@login_required
def get_booking(booking_id: int) -> Any:
    booking = (
        Booking.query.filter_by(id=dehumanize(booking_id)).options(joinedload(Booking.individualBooking)).first_or_404()
    )
    booking.userId = booking.individualBooking.userId

    return jsonify(as_dict(booking, includes=WEBAPP_GET_BOOKING_INCLUDES)), 200
