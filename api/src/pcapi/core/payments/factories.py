import factory

from pcapi.core.payments import conf as deposit_conf
from pcapi.core.testing import BaseFactory
from pcapi.core.users.factories import DepositGrantFactory

from . import models


class RecreditFactory(BaseFactory):
    class Meta:
        model = models.Recredit

    deposit = factory.SubFactory(DepositGrantFactory)
    amount = factory.LazyAttribute(lambda recredit: deposit_conf.RECREDIT_TYPE_AMOUNT_MAPPING[recredit.recreditType])
    recreditType = models.RecreditType.RECREDIT_16
