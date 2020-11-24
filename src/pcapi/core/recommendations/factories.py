import factory

from pcapi import models
import pcapi.core.offers.factories as offers_factories
from pcapi.core.testing import BaseFactory
import pcapi.core.users.factories as users_factories


class RecommendationFactory(BaseFactory):
    class Meta:
        model = models.Recommendation

    user = factory.SubFactory(users_factories.UserFactory)
    mediation = factory.SubFactory(offers_factories.MediationFactory)
    offer = factory.Maybe(
        "mediation",
        factory.SelfAttribute("mediation.offer"),
        factory.SubFactory(offers_factories.OfferFactory),
    )
