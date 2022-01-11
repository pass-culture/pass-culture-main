import random

import factory

from pcapi.core import testing
import pcapi.core.users.factories as users_factories

from . import models


class SubscriptionMessageFactory(testing.BaseFactory):
    class Meta:
        model = models.SubscriptionMessage

    user = factory.SubFactory(users_factories.UserFactory)
    userMessage = factory.Faker("sentence", nb_words=3)
    callToActionTitle = factory.Sequence("Call To Action title #{0}".format)
    callToActionLink = factory.Sequence("https://ctalink.example.com/{0}".format)
    callToActionIcon = factory.LazyAttribute(lambda o: random.choice(list(models.CallToActionIcon)))
    popOverIcon = factory.LazyAttribute(lambda o: random.choice(list(models.PopOverIcon)))
