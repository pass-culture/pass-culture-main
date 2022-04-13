import factory

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
from pcapi.core.testing import BaseFactory

from . import models


class CriterionFactory(BaseFactory):
    class Meta:
        model = models.Criterion

    name = factory.Sequence("Criterion_{}".format)


class VenueCriterionFactory(BaseFactory):
    class Meta:
        model = models.VenueCriterion

    venue = factory.SubFactory(offerers_factories.VenueFactory)
    criterion = factory.SubFactory(CriterionFactory)


class OfferCriterionFactory(BaseFactory):
    class Meta:
        model = models.OfferCriterion

    offer = factory.SubFactory(offers_factories.OfferFactory)
    criterion = factory.SubFactory(CriterionFactory)
