import factory.fuzzy

from pcapi.core.factories import BaseFactory
from pcapi.utils.date import get_department_timezone
from pcapi.utils.regions import get_department_code_from_city_code

from . import models


class IrisFranceFactory(factory.Factory):
    class Meta:
        model = models.IrisFrance


class AddressFactory(BaseFactory):
    class Meta:
        model = models.Address
        sqlalchemy_get_or_create = ("street", "inseeCode")

    banId = "75102_7560_00001"
    inseeCode = factory.LazyAttribute(lambda address: address.banId.split("_")[0] if address.banId else None)
    street = factory.Sequence("1{} boulevard Poissonnière".format)  # sequence avoids UniqueViolation (street+inseeCode)
    postalCode = "75002"
    city = "Paris"
    latitude: float | None = 48.87055
    longitude: float | None = 2.3476515
    departmentCode = factory.LazyAttribute(
        lambda address: (
            get_department_code_from_city_code(address.inseeCode or address.postalCode)
            if address.inseeCode or address.postalCode
            else None
        )
    )
    timezone = factory.LazyAttribute(lambda address: get_department_timezone(address.departmentCode))
    isManualEdition = False
