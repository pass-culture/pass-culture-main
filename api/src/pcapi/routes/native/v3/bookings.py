import logging

from flask_login import current_user

import pcapi.core.bookings.api as bookings_api
from pcapi.models.api_errors import ResourceNotFoundError
from pcapi.routes.native.security import authenticated_and_active_user_required
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils.transaction_manager import atomic

from .. import blueprint
from .serialization import bookings as serializers


logger = logging.getLogger(__name__)


@blueprint.native_route("/bookings/<int:booking_id>", version="v3", methods=["GET"])
@spectree_serialize(
    on_success_status=200,
    api=blueprint.api,
    response_model=serializers.BookingResponseV3,
    on_error_statuses=[404],
    deprecated=True,
)
@authenticated_and_active_user_required
@atomic()
def get_booking(booking_id: int) -> serializers.BookingResponseV3:
    booking = bookings_api.get_booking_by_id(current_user, booking_id)
    if booking is None:
        raise ResourceNotFoundError()
    return serializers.BookingResponseV3.build(booking)
