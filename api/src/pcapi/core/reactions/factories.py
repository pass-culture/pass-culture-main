import typing

from factory import SubFactory

from pcapi.core.factories import BaseFactory
from pcapi.core.users.factories import UserFactory

from . import models


class ReactionFactory(BaseFactory):
    class Meta:
        model = models.Reaction

    reactionType = models.ReactionTypeEnum.NO_REACTION
    user = SubFactory(UserFactory)
    offer = None
    product = None

    @classmethod
    def _create(cls, model_class: type[models.Reaction], *args: typing.Any, **kwargs: typing.Any) -> models.Reaction:
        reaction = super()._create(model_class, *args, **kwargs)
        if not reaction.offer and not reaction.product:
            raise ValueError("A reaction should be linked to a product or an offer.")
        return reaction
