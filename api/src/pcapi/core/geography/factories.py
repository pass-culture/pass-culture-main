import factory.fuzzy

from pcapi.core.factories import BaseFactory
from pcapi.utils.date import METROPOLE_TIMEZONE

from . import models


class IrisFranceFactory(factory.Factory):
    class Meta:
        model = models.IrisFrance


class AddressFactory(BaseFactory):
    street = factory.Sequence("1{} boulevard Poissonnière".format)  # sequence avoids UniqueViolation (street+inseeCode)
    postalCode = "75002"
    city = "Paris"
    latitude: float | None = 48.87055
    longitude: float | None = 2.3476515
    inseeCode = "75102"
    banId = "75102_7560_00001"
    timezone = METROPOLE_TIMEZONE

    class Meta:
        model = models.Address
        sqlalchemy_get_or_create = ["street", "inseeCode"]
