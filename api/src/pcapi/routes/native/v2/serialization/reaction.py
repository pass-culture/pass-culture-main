import datetime

from pcapi.core.reactions.models import ReactionTypeEnum
from pcapi.routes.serialization import HttpBodyModel


class PostOneReactionRequest(HttpBodyModel):
    offer_id: int
    reaction_type: ReactionTypeEnum


class PostReactionRequest(HttpBodyModel):
    reactions: list[PostOneReactionRequest]


class AvailableReactionBooking(HttpBodyModel):
    dateUsed: datetime.datetime | None
    image: str | None
    name: str
    offer_id: int
    subcategory_id: str


class GetAvailableReactionsResponse(HttpBodyModel):
    bookings: list[AvailableReactionBooking]
    number_of_reactable_bookings: int
