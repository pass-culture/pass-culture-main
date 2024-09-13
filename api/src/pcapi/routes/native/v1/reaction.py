import logging

import pcapi.core.reactions.api as reactions_api
import pcapi.core.users.models as users_models
from pcapi.repository import atomic
from pcapi.routes.native.security import authenticated_and_active_user_required
import pcapi.routes.native.v1.serialization.reaction as serialization
from pcapi.serialization.decorator import spectree_serialize

from .. import blueprint


logger = logging.getLogger(__name__)


@blueprint.native_route("/reaction", methods=["POST"])
@spectree_serialize(api=blueprint.api, on_success_status=204)
@authenticated_and_active_user_required
@atomic()
def post_reaction(user: users_models.User, body: serialization.PostReactionRequest) -> None:
    reactions_api.bulk_update_or_create_reaction(user, body.reactions)


@blueprint.native_route("/reaction/available", methods=["GET"])
@spectree_serialize(api=blueprint.api)
@authenticated_and_active_user_required
def get_available_reactions(user: users_models.User) -> serialization.GetAvailableReactionsResponse:
    booking_with_available_reactions = reactions_api.get_booking_with_available_reactions(user.id)

    return serialization.GetAvailableReactionsResponse(
        bookings=[
            serialization.AvailableReactionBooking(
                name=booking.stock.offer.name,
                dateUsed=booking.dateUsed,
                image=booking.stock.offer.image.url if booking.stock.offer.image else None,
            )
            for booking in booking_with_available_reactions
        ]
    )
