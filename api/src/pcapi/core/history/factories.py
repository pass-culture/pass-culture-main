import factory

from pcapi.core.history import models
from pcapi.core.testing import BaseFactory
import pcapi.core.users.factories as users_factories


class ActionHistoryFactory(BaseFactory):
    class Meta:
        model = models.ActionHistory

    actionType = models.ActionType.COMMENT
    authorUser = factory.SubFactory(users_factories.AdminFactory)
    comment = factory.Sequence(lambda n: f"Action #{n:04} created by factory")
