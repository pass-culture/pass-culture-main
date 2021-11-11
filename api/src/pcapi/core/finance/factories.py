import factory

from pcapi.core.testing import BaseFactory

from . import models


class BusinessUnitFactory(BaseFactory):
    class Meta:
        model = models.BusinessUnit

    name = factory.Sequence("Business unit #{}".format)
    siret = factory.Sequence("{:014}".format)

    bankAccount = factory.SubFactory("pcapi.core.offers.factories.BankInformationFactory")
