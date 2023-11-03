import enum
import logging

from pydantic.v1 import ValidationError
import sqlalchemy as sa

from pcapi.core.educational import models as educational_models
from pcapi.core.educational.exceptions import MissingRequiredRedactorInformation
from pcapi.routes.serialization import BaseModel

from .redactor import RedactorPreferences


logger = logging.getLogger(__name__)


class AdageFrontRoles(enum.Enum):
    REDACTOR = "redactor"
    READONLY = "readonly"


class AuthenticatedInformation(BaseModel):
    civility: str | None
    lastname: str | None
    firstname: str | None
    email: str
    uai: str | None
    lat: float | None
    lon: float | None


class AuthenticatedResponse(BaseModel):
    role: AdageFrontRoles
    uai: str | None = None
    departmentCode: str | None = None
    institutionName: str | None = None
    institutionCity: str | None = None
    email: str | None = None
    preferences: RedactorPreferences | None = None
    lat: float | None = None
    lon: float | None = None
    favoritesCount: int = 0
    offersCount: int = 0

    class Config:
        use_enum_values = True


class RedactorInformation(BaseModel):
    civility: str | None
    lastname: str | None
    firstname: str | None
    email: str
    uai: str


def get_redactor_information_from_adage_authentication(
    authenticated_information: AuthenticatedInformation,
) -> RedactorInformation:
    try:
        redactor_information: RedactorInformation = RedactorInformation(**authenticated_information.dict())
    except ValidationError:
        raise MissingRequiredRedactorInformation()
    return redactor_information


def get_offers_count(authenticated_information: AuthenticatedInformation) -> int:
    offer_query = (
        educational_models.CollectiveOffer.query.join(
            educational_models.EducationalInstitution, educational_models.CollectiveOffer.institution
        )
        .options(
            sa.orm.joinedload(educational_models.CollectiveOffer.collectiveStock).joinedload(
                educational_models.CollectiveStock.collectiveBookings
            ),
        )
        .filter(educational_models.EducationalInstitution.institutionId == authenticated_information.uai)
    )
    offer_count = len([query for query in offer_query if query.isBookable])
    return offer_count
