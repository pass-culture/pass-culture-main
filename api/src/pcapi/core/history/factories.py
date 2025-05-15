from datetime import datetime

import factory
from dateutil.relativedelta import relativedelta

import pcapi.core.users.constants as users_constants
import pcapi.core.users.factories as users_factories
from pcapi.core.factories import BaseFactory
from pcapi.core.history import models


class ActionHistoryFactory(BaseFactory):
    class Meta:
        model = models.ActionHistory

    actionType = models.ActionType.COMMENT
    authorUser = factory.SubFactory(users_factories.AdminFactory)
    comment = factory.Sequence(lambda n: f"Action #{n:04} created by factory")


class SuspendedUserActionHistoryFactory(ActionHistoryFactory):
    class Params:
        reason = users_constants.SuspensionReason.FRAUD_SUSPICION

    user = factory.SubFactory(
        users_factories.UserFactory, isActive=False, dateCreated=datetime.utcnow() - relativedelta(days=2)
    )
    actionType = models.ActionType.USER_SUSPENDED
    actionDate = factory.LazyFunction(lambda: datetime.utcnow() - relativedelta(days=1))
    extraData = factory.LazyAttribute(lambda o: {"reason": o.reason.value})


class UnsuspendedUserActionHistoryFactory(ActionHistoryFactory):
    user = factory.SubFactory(users_factories.UserFactory)
    actionType = models.ActionType.USER_UNSUSPENDED
    actionDate = factory.LazyFunction(lambda: datetime.utcnow() - relativedelta(days=1))


class BlacklistDomainNameFactory(ActionHistoryFactory):
    actionType = models.ActionType.BLACKLIST_DOMAIN_NAME
