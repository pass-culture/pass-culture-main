import logging

from flask_login import current_user
from flask_login import login_required

from pcapi.core.educational import exceptions as collective_exceptions
from pcapi.core.educational.api import booking as educational_api_booking
from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import exceptions as offerers_exceptions
from pcapi.models.api_errors import ApiErrors
from pcapi.routes.apis import private_api
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils.rest import check_user_has_access_to_offerer
from pcapi.utils.transaction_manager import atomic

from . import blueprint


logger = logging.getLogger(__name__)


@private_api.route("/collective/offers/<int:offer_id>/cancel_booking", methods=["PATCH"])
@login_required
@spectree_serialize(
    on_success_status=204,
    on_error_statuses=[400, 403, 404],
    api=blueprint.pro_private_schema,
)
@atomic()
def cancel_collective_offer_booking(offer_id: int) -> None:
    try:
        offerer = offerers_api.get_offerer_by_collective_offer_id(offer_id)
    except offerers_exceptions.CannotFindOffererForOfferId:
        raise ApiErrors(
            {"code": "NO_COLLECTIVE_OFFER_FOUND", "message": "No collective offer has been found with this id"}, 404
        )
    check_user_has_access_to_offerer(current_user, offerer.id)

    try:
        educational_api_booking.cancel_collective_offer_booking(
            offer_id, current_user.real_user.id, current_user.is_impersonated
        )
    except collective_exceptions.CollectiveStockNotFound:
        raise ApiErrors(
            {"code": "NO_ACTIVE_STOCK_FOUND", "message": "No active stock has been found with this id"}, 404
        )
    except collective_exceptions.CollectiveOfferNotFound:
        raise ApiErrors(
            {"code": "NO_COLLECTIVE_OFFER_FOUND", "message": "No collective offer has been found with this id"}, 404
        )
    except collective_exceptions.NoCollectiveBookingToCancel:
        raise ApiErrors({"code": "NO_BOOKING", "message": "This collective offer has no booking to cancel"}, 400)
    except collective_exceptions.CollectiveOfferForbiddenAction:
        raise ApiErrors(
            {"code": "CANCEL_NOT_ALLOWED", "message": "This collective offer status does not allow cancellation"}, 403
        )
