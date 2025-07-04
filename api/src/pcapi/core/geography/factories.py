import factory.fuzzy

from pcapi.core.factories import BaseFactory
from pcapi.utils.date import get_department_timezone
from pcapi.utils.regions import get_department_code_from_city_code

from . import models


DEFAULT_LATITUDE = 48.87055
DEFAULT_LONGITUDE = 2.3476515
DEFAULT_TRUNCATED_LONGITUDE = 2.34765


class IrisFranceFactory(factory.Factory):
    class Meta:
        model = models.IrisFrance


class AddressFactory(BaseFactory):
    class Meta:
        model = models.Address
        sqlalchemy_get_or_create = ("street", "inseeCode")

    banId: str | None = "75102_7560_00001"
    inseeCode: str | factory.declarations.BaseDeclaration | None = factory.LazyAttribute(
        lambda address: address.banId.split("_")[0] if address.banId else None
    )
    street: str | factory.declarations.BaseDeclaration | None = factory.Sequence(
        "1{} boulevard Poissonnière".format
    )  # sequence avoids UniqueViolation (street+inseeCode)
    postalCode: str = "75002"
    city: str = "Paris"
    latitude: float | None = DEFAULT_LATITUDE
    longitude: float | None = DEFAULT_LONGITUDE
    departmentCode = factory.LazyAttribute(
        lambda address: (
            get_department_code_from_city_code(address.inseeCode or address.postalCode)
            if address.inseeCode or address.postalCode
            else None
        )
    )
    timezone = factory.LazyAttribute(lambda address: get_department_timezone(address.departmentCode))
    isManualEdition = False


class ManualAddressFactory(AddressFactory):
    banId = None
    inseeCode = None
    isManualEdition = True


class CaledonianAddressFactory(AddressFactory):
    street: str | factory.declarations.BaseDeclaration | None = factory.Sequence(
        "{} Avenue James Cook".format
    )  # sequence avoids UniqueViolation (street+inseeCode)
    postalCode: str = "98800"
    city: str = "Nouméa"
    latitude: float | None = -22.26355
    longitude: float | None = 166.4146
    banId: str = "98818_w65mkd"
