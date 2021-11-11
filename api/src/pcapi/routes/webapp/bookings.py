from typing import Any

from flask import abort
from flask import jsonify
from flask_login import current_user
from flask_login import login_required
from sqlalchemy.orm import joinedload

import pcapi.core.bookings.api as bookings_api
from pcapi.core.bookings.models import Booking
from pcapi.core.offers.exceptions import StockDoesNotExist
from pcapi.infrastructure.container import get_bookings_for_beneficiary
from pcapi.models.feature import FeatureToggle
from pcapi.routes.apis import private_api
from pcapi.routes.serialization import as_dict
from pcapi.routes.serialization.beneficiary_bookings_serialize import serialize_beneficiary_bookings
from pcapi.routes.serialization.bookings_serialize import PostBookingBodyModel
from pcapi.routes.serialization.bookings_serialize import PostBookingResponseModel
from pcapi.routes.serialization.bookings_serialize import serialize_booking_minimal
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils.human_ids import dehumanize
from pcapi.utils.includes import WEBAPP_GET_BOOKING_INCLUDES
from pcapi.utils.rest import expect_json_data


@private_api.route("/bookings", methods=["GET"])
@login_required
def get_bookings() -> Any:
    beneficiary_bookings = get_bookings_for_beneficiary.execute(current_user.id)
    serialize_with_qr_code = FeatureToggle.QR_CODE.is_active()
    serialized_bookings = serialize_beneficiary_bookings(beneficiary_bookings, with_qr_code=serialize_with_qr_code)
    return jsonify(serialized_bookings), 200


@private_api.route("/bookings/<booking_id>", methods=["GET"])
@login_required
def get_booking(booking_id: int) -> Any:
    booking = (
        Booking.query.filter_by(id=dehumanize(booking_id)).options(joinedload(Booking.individualBooking)).first_or_404()
    )
    booking.userId = booking.individualBooking.userId

    return jsonify(as_dict(booking, includes=WEBAPP_GET_BOOKING_INCLUDES)), 200


@private_api.route("/bookings", methods=["POST"])
@login_required
@expect_json_data
@spectree_serialize(response_model=PostBookingResponseModel, on_success_status=201)
def create_booking(body: PostBookingBodyModel) -> PostBookingResponseModel:
    if not body.stock_id:
        abort(404)

    try:
        booking = bookings_api.book_offer(
            beneficiary=current_user,
            stock_id=dehumanize(body.stock_id),
            quantity=body.quantity,
        )
    except StockDoesNotExist:
        abort(404)

    return PostBookingResponseModel(**serialize_booking_minimal(booking))


@private_api.route("/bookings/<booking_id>/cancel", methods=["PUT"])
@login_required
def cancel_booking(booking_id: str) -> Any:
    booking = Booking.query.filter_by(id=dehumanize(booking_id)).first_or_404()

    bookings_api.cancel_booking_by_beneficiary(current_user, booking)

    return jsonify(serialize_booking_minimal(booking)), 200
