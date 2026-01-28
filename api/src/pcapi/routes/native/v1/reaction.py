import logging

from flask_login import current_user

import pcapi.core.reactions.api as reactions_api
import pcapi.routes.native.v1.serialization.reaction as serialization
from pcapi.core.reactions import exceptions as reactions_exceptions
from pcapi.models.api_errors import ApiErrors
from pcapi.routes.native.security import authenticated_and_active_user_required
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils.transaction_manager import atomic

from .. import blueprint


logger = logging.getLogger(__name__)


@blueprint.native_route("/reaction", methods=["POST"])
@spectree_serialize(api=blueprint.api, on_success_status=204)
@authenticated_and_active_user_required
@atomic()
def post_reaction(body: serialization.PostReactionRequest) -> None:
    try:
        reactions_api.bulk_update_or_create_reaction(current_user, body.reactions)
    except reactions_exceptions.OfferNotBooked:
        raise ApiErrors({"code": "OFFER_NOT_BOOKED"})
    except reactions_exceptions.CanNotReact:
        raise ApiErrors({"code": "CAN_NOT_REACT"})


@blueprint.native_route("/reaction/available", methods=["GET"])
@spectree_serialize(api=blueprint.api, response_model=serialization.GetAvailableReactionsResponse)
@authenticated_and_active_user_required
def get_available_reactions() -> serialization.GetAvailableReactionsResponse:
    booking_with_available_reactions = reactions_api.get_bookings_with_available_reactions(current_user.id)

    return serialization.GetAvailableReactionsResponse(
        number_of_reactable_bookings=len(booking_with_available_reactions),
        bookings=[
            serialization.AvailableReactionBooking(
                name=booking.stock.offer.name,
                offer_id=booking.stock.offer.id,
                subcategory_id=booking.stock.offer.subcategoryId,
                dateUsed=booking.dateUsed,
                image=booking.stock.offer.image.url if booking.stock.offer.image else None,
            )
            for booking in booking_with_available_reactions
        ],
    )
