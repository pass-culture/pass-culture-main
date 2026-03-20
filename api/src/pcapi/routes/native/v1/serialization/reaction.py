import datetime
import logging

from pcapi.core.reactions.models import ReactionTypeEnum
from pcapi.routes.serialization import HttpBodyModel


logger = logging.getLogger(__name__)


class PostOneReactionRequest(HttpBodyModel):
    offer_id: int
    reaction_type: ReactionTypeEnum


class PostReactionRequest(HttpBodyModel):
    reactions: list[PostOneReactionRequest]


class AvailableReactionBooking(HttpBodyModel):
    name: str
    offer_id: int
    subcategory_id: str
    image: str | None = None

    dateUsed: datetime.datetime | None = None


class GetAvailableReactionsResponse(HttpBodyModel):
    number_of_reactable_bookings: int
    bookings: list[AvailableReactionBooking]
