import typing

from pcapi.core.reactions.models import ReactionTypeEnum
from pcapi.routes.serialization import ConfiguredBaseModel


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
