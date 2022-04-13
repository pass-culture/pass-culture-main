import factory

from pcapi.core.testing import BaseFactory

from . import models


class CriterionFactory(BaseFactory):
    class Meta:
        model = models.Criterion

    name = factory.Sequence("Criterion_{}".format)
