import factory

import pcapi.core.offers.factories as offers_factories
from pcapi.core.testing import BaseFactory

from . import models


class CriterionFactory(BaseFactory):
    class Meta:
        model = models.Criterion

    name = factory.Sequence("Criterion_{}".format)


class OfferCriterionFactory(BaseFactory):
    class Meta:
        model = models.OfferCriterion

    offer = factory.SubFactory(offers_factories.OfferFactory)
    criterion = factory.SubFactory(CriterionFactory)
