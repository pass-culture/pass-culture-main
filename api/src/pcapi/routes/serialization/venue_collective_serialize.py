import enum
import typing
from datetime import datetime

import typing
import pydantic.v1 as pydantic_v1
from pydantic.v1 import validator
import pydantic
from pydantic import field_validator
from pcapi.serialization.exceptions import PydanticError
from pcapi.core.educational import models as educational_models
from pcapi.core.educational.constants import ALL_INTERVENTION_AREA
from pcapi.core.offerers import models as offerers_models
from pcapi.routes.serialization import BaseModel
from pcapi.routes.serialization import HttpBodyModel
from pcapi.routes.shared.collective.serialization import offers as shared_offers
from pcapi.utils.date import format_into_utc_date


class DMSApplicationstatus(enum.Enum):
    ACCEPTED = "accepte"
    DROPPED = "sans_suite"
    BUILDING = "en_construction"
    REFUSED = "refuse"
    INSTRUCTING = "en_instruction"


class DMSApplicationForEACv1(BaseModel):
    venueId: int
    state: DMSApplicationstatus
    procedure: int
    application: int
    lastChangeDate: datetime
    depositDate: datetime
    expirationDate: datetime | None
    buildDate: datetime | None
    instructionDate: datetime | None
    processingDate: datetime | None
    userDeletionDate: datetime | None

    class Config:
        orm_mode = True
        json_encoders = {datetime: format_into_utc_date}

    @classmethod
    def from_orm(  # type: ignore[override]
        cls, collective_dms_application: educational_models.CollectiveDmsApplication, venue_id: int
    ) -> typing.Self:
        collective_dms_application.venueId = venue_id  # type: ignore [attr-defined]
        return super().from_orm(collective_dms_application)


class DMSApplicationForEAC(HttpBodyModel):
    venueId: int
    state: DMSApplicationstatus
    procedure: int
    application: int
    lastChangeDate: datetime
    depositDate: datetime
    expirationDate: datetime | None
    buildDate: datetime | None
    instructionDate: datetime | None
    processingDate: datetime | None
    userDeletionDate: datetime | None

    @classmethod
    def build(
        cls, collective_dms_application: educational_models.CollectiveDmsApplication, venue_id: int
    ) -> typing.Self:
        return cls(
            venueId=venue_id,
            state=collective_dms_application.state,
            procedure=collective_dms_application.procedure,
            application=collective_dms_application.application,
            lastChangeDate=collective_dms_application.lastChangeDate,
            depositDate=collective_dms_application.depositDate,
            expirationDate=collective_dms_application.expirationDate,
            buildDate=collective_dms_application.buildDate,
            instructionDate=collective_dms_application.instructionDate,
            processingDate=collective_dms_application.processingDate,
            userDeletionDate=collective_dms_application.userDeletionDate,
        )


class GetVenueDomainResponseModel(HttpBodyModel):
    id: int
    name: str


class LegalStatusResponseModel(HttpBodyModel):
    id: int
    name: str


class EditVenueCollectiveDataBodyModel(HttpBodyModel):
    collectiveDescription: typing.Annotated[str | None, pydantic.Field(pre=False, allow_reuse=True, max_length=500)] = (
        None
    )
    collectiveStudents: list[educational_models.StudentLevels] | None = None
    collectiveWebsite: typing.Annotated[str | None, pydantic.Field(pre=False, allow_reuse=True, max_length=150)] = None
    collectiveDomains: list[int] | None = None
    collectiveInterventionArea: list[str] | None = None
    venueEducationalStatusId: int | None = None
    collectiveNetwork: list[str] | None = None
    collectiveAccessInformation: typing.Annotated[
        str | None, pydantic.Field(pre=False, allow_reuse=True, max_length=500)
    ] = None
    collectivePhone: typing.Annotated[str | None, pydantic.Field(pre=False, allow_reuse=True, max_length=50)] = (
        None  # TODO  bulle why 50?
    )
    collectiveEmail: typing.Annotated[str | None, pydantic.Field(pre=False, allow_reuse=True, max_length=150)] = None
    activity: offerers_models.ActivityOpenToPublic | offerers_models.ActivityNotOpenToPublic | None = None

    @field_validator("collectiveStudents", mode="after")
    @classmethod
    def validate_collectiveStudents(cls, students: list[str]) -> list[educational_models.StudentLevels] | None:
        if not students:
            return []
        return shared_offers.validate_students(students)

    @field_validator("collectiveInterventionArea", mode="after")
    @classmethod
    def validate_collectiveInterventionArea(cls, intervention_area: list[str] | None) -> list[str] | None:
        if intervention_area and any(area not in ALL_INTERVENTION_AREA for area in intervention_area):
            raise ValueError("One or more element is not a valid area")

        return intervention_area


# TODO bulle voir pour simplifier?
class VenuesEducationalStatusResponseModel(HttpBodyModel):
    id: int
    name: str


class VenuesEducationalStatusesResponseModel(HttpBodyModel):
    statuses: list[VenuesEducationalStatusResponseModel]
