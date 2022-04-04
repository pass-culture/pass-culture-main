import datetime

import factory

import pcapi.core.offers.factories as offers_factories
from pcapi.core.payments import conf as deposit_conf
from pcapi.core.testing import BaseFactory
from pcapi.core.users.factories import DepositGrantFactory

from . import models


class CustomReimbursementRuleFactory(BaseFactory):
    class Meta:
        model = models.CustomReimbursementRule

    offer = factory.SubFactory(offers_factories.OfferFactory)
    timespan = factory.LazyFunction(
        lambda: [
            datetime.datetime.utcnow() - datetime.timedelta(days=365),
            datetime.datetime.utcnow() + datetime.timedelta(days=365),
        ]
    )
    amount = 5

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        if "rate" in kwargs:
            kwargs["amount"] = None
        if "offerer" in kwargs:
            kwargs["offer"] = None
        return super()._create(model_class, *args, **kwargs)


class RecreditFactory(BaseFactory):
    class Meta:
        model = models.Recredit

    deposit = factory.SubFactory(DepositGrantFactory)
    amount = factory.LazyAttribute(lambda recredit: deposit_conf.RECREDIT_TYPE_AMOUNT_MAPPING[recredit.recreditType])
    recreditType = models.RecreditType.RECREDIT_16
