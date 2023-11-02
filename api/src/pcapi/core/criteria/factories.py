import factory

from pcapi.core.factories import BaseFactory

from . import models


class CriterionFactory(BaseFactory):
    class Meta:
        model = models.Criterion

    name = factory.Sequence("Criterion_{}".format)


class CriterionCategoryFactory(BaseFactory):
    class Meta:
        model = models.CriterionCategory

    label = factory.Sequence("Criterion category {}".format)


class OfferCriterionFactory(BaseFactory):
    class Meta:
        model = models.OfferCriterion


class VenueCriterionFactory(BaseFactory):
    class Meta:
        model = models.VenueCriterion
