import factory.fuzzy

from pcapi.core.factories import BaseFactory

from . import models


class IrisFranceFactory(factory.Factory):
    class Meta:
        model = models.IrisFrance


class AddressFactory(BaseFactory):
    class Meta:
        model = models.Address
