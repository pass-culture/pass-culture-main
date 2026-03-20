import enum
import typing
from datetime import datetime

import pydantic.v1 as pydantic_v1
from pydantic.v1 import validator

from pcapi.core.educational import models as educational_models
from pcapi.core.educational.constants import ALL_INTERVENTION_AREA
from pcapi.core.offerers import models as offerers_models
from pcapi.routes.serialization import BaseModel
from pcapi.routes.serialization import HttpBodyModel
from pcapi.routes.shared.collective.serialization import offers as shared_offers
from pcapi.serialization.utils import string_length_validator
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


class EditVenueCollectiveDataBodyModel(BaseModel):
    collectiveDescription: str | None
    collectiveStudents: list[educational_models.StudentLevels] | None
    collectiveWebsite: str | None
    collectiveDomains: list[int] | None
    collectiveInterventionArea: list[str] | None
    venueEducationalStatusId: int | None
    collectiveNetwork: list[str] | None
    collectiveAccessInformation: str | None
    collectivePhone: str | None
    collectiveEmail: str | None
    activity: offerers_models.ActivityOpenToPublic | offerers_models.ActivityNotOpenToPublic | None

    _validate_collectiveDescription = string_length_validator("collectiveDescription", length=500)
    _validate_collectiveWebsite = string_length_validator("collectiveWebsite", length=150)
    _validate_collectiveAccessInformation = string_length_validator("collectiveAccessInformation", length=500)
    _validate_collectivePhone = string_length_validator("collectivePhone", length=50)
    _validate_collectiveEmail = string_length_validator("collectiveEmail", length=150)

    @validator("collectiveStudents")
    def validate_students(cls, students: list[str]) -> list[educational_models.StudentLevels] | None:
        if not students:
            return []
        return shared_offers.validate_students(students)

    @validator("collectiveInterventionArea")
    def validate_intervention_area(cls, intervention_area: list[str] | None) -> list[str] | None:
        if intervention_area and any(area not in ALL_INTERVENTION_AREA for area in intervention_area):
            raise ValueError("One or more element is not a valid area")

        return intervention_area


class VenuesEducationalStatusResponseModel(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True
        extra = pydantic_v1.Extra.forbid


class VenuesEducationalStatusesResponseModel(BaseModel):
    statuses: list[VenuesEducationalStatusResponseModel]
