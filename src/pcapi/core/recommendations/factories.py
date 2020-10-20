import factory

from pcapi.core.testing import BaseFactory

import pcapi.core.offers.factories as offers_factories
import pcapi.core.users.factories as users_factories
from pcapi import models


class MediationFactory(BaseFactory):
    class Meta:
        model = models.MediationSQLEntity

    offer = factory.SubFactory(offers_factories.OfferFactory)
    isActive = True


class RecommendationFactory(BaseFactory):
    class Meta:
        model = models.Recommendation

    user = factory.SubFactory(users_factories.UserFactory)
    mediation = factory.SubFactory(MediationFactory)
    offer = factory.SelfAttribute('mediation.offer')
