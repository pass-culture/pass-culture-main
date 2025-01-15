import datetime
import logging
import typing

from pcapi.core.reactions.models import ReactionTypeEnum
from pcapi.routes.serialization import ConfiguredBaseModel


logger = logging.getLogger(__name__)


class PostOneReactionRequest(ConfiguredBaseModel):
    offer_id: int
    reaction_type: ReactionTypeEnum


class PostReactionRequest(ConfiguredBaseModel):
    reactions: list[PostOneReactionRequest]

    def __init__(self, **kwargs: typing.Any) -> None:
        # Handle the case where the user sends a single PostOneReactionRequest
        if "offerId" in kwargs:
            kwargs["reactions"] = [PostOneReactionRequest(**kwargs)]
            del kwargs["offerId"]
            del kwargs["reactionType"]
        super().__init__(**kwargs)


class AvailableReactionBooking(ConfiguredBaseModel):
    name: str
    offer_id: int
    subcategory_id: str
    image: str | None
    dateUsed: datetime.datetime | None


class GetAvailableReactionsResponse(ConfiguredBaseModel):
    number_of_reactable_bookings: int
    bookings: list[AvailableReactionBooking]
