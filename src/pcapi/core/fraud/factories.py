import random

import factory

from pcapi.core import testing
import pcapi.core.users.factories as users_factories

from . import models


class BeneficiaryFraudCheckFactory(testing.BaseFactory):
    class Meta:
        model = models.BeneficiaryFraudCheck

    user = factory.SubFactory(users_factories.UserFactory)
    type = factory.LazyAttribute(lambda o: random.choice(list(models.FraudCheckType)))
    thirdPartyId = factory.Sequence("ThirdPartyIdentifier-{0}".format)

    # todo : create pydantic factories and a hook to create the right type with the right factory
    # resultContent =


class BeneficiaryFraudResultFactory(testing.BaseFactory):
    class Meta:
        model = models.BeneficiaryFraudResult

    user = factory.SubFactory(users_factories.UserFactory)
    status = factory.LazyAttribute(lambda o: random.choice(list(models.FraudStatus)).value)
    reason = factory.Sequence("Fraud Result excuse #{0}".format)
