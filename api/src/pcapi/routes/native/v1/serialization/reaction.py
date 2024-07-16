import datetime
import logging

from pcapi.core.reactions.models import ReactionTypeEnum
from pcapi.routes.serialization import ConfiguredBaseModel


logger = logging.getLogger(__name__)


class PostReactionRequest(ConfiguredBaseModel):
    offer_id: int
    reaction_type: ReactionTypeEnum


class AvailableReactionBooking(ConfiguredBaseModel):
    name: str
    image: str | None
    dateUsed: datetime.datetime | None


class GetAvailableReactionsResponse(ConfiguredBaseModel):
    bookings: list[AvailableReactionBooking]
