import datetime

import factory

from pcapi.core.factories import BaseFactory
import pcapi.core.users.factories as users_factories

from . import models


class AchievementFactory(BaseFactory):
    class Meta:
        model = models.Achievement

    slug = factory.Sequence(lambda n: f"slug-{n}")
    name = factory.Sequence(lambda n: f"name-{n}")
    description = factory.Sequence(lambda n: f"description-{n}")
    category = factory.Sequence(lambda n: f"category-{n}")
    icon = factory.Sequence(lambda n: f"icon-{n}")


class UserAchievementFactory(BaseFactory):
    class Meta:
        model = models.UserAchievement

    user = factory.SubFactory(users_factories.BeneficiaryFactory)
    achievement = factory.SubFactory(AchievementFactory)
    completionDate = factory.LazyFunction(datetime.datetime.utcnow)
