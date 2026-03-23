import enum
import typing
from datetime import datetime

import pydantic as pydantic_v2
from pydantic import field_validator

from pcapi.core.educational import models as educational_models
from pcapi.core.educational.constants import ALL_INTERVENTION_AREA
from pcapi.core.offerers import models as offerers_models
from pcapi.routes.serialization import BaseModel
from pcapi.routes.serialization import HttpBodyModel
from pcapi.routes.shared.collective.serialization import offers as shared_offers
from pcapi.serialization.exceptions import PydanticError
from pcapi.utils.date import format_into_utc_date


class DMSApplicationstatus(enum.Enum):
    ACCEPTED = "accepte"
    DROPPED = "sans_suite"
    BUILDING = "en_construction"
    REFUSED = "refuse"
    INSTRUCTING = "en_instruction"


# TODO bdalbianco 23/03/2026 delete when getvenueresponsemodel is migrated
class DMSApplicationForEAC(BaseModel):
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


class DMSApplicationForEACv2(HttpBodyModel):
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


# TODO bdalbianco 23/03/2026 delete when getvenueresponsemodel is migrated
class GetVenueDomainResponseModel(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class GetVenueDomainResponseModelv2(HttpBodyModel):
    id: int
    name: str


# TODO bdalbianco 23/03/2026 delete when getvenueresponsemodel is migrated
class LegalStatusResponseModel(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class LegalStatusResponseModelv2(HttpBodyModel):
    id: int
    name: str


class EditVenueCollectiveDataBodyModel(HttpBodyModel):
    collectiveDescription: str | None = pydantic_v2.Field(None, max_length=500)
    collectiveStudents: list[educational_models.StudentLevels] | None = None
    collectiveWebsite: str | None = pydantic_v2.Field(None, max_length=150)
    collectiveDomains: list[int] | None = None
    collectiveInterventionArea: list[str] | None = None
    venueEducationalStatusId: int | None = None
    collectiveNetwork: list[str] | None = None
    collectiveAccessInformation: str | None = pydantic_v2.Field(None, max_length=500)
    collectivePhone: str | None = pydantic_v2.Field(None, max_length=50)
    collectiveEmail: str | None = pydantic_v2.Field(None, max_length=150)
    activity: offerers_models.ActivityOpenToPublic | offerers_models.ActivityNotOpenToPublic | None = None

    @field_validator("collectiveStudents", mode="after")
    @classmethod
    def validate_collectiveStudents(
        cls, students: list[educational_models.StudentLevels] | None
    ) -> list[educational_models.StudentLevels] | None:
        if not students:
            return []
        try:
            # TODO (jcicurel-pass, 2026-02-04): refactor validate_students to raise correct error
            # when all models using it are migrated to v2
            shared_offers.validate_students(students)
        except ValueError as ex:
            raise PydanticError(str(ex))
        return students

    @field_validator("collectiveInterventionArea", mode="after")
    @classmethod
    def validate_collectiveInterventionArea(cls, intervention_area: list[str] | None) -> list[str] | None:
        if intervention_area and any(area not in ALL_INTERVENTION_AREA for area in intervention_area):
            raise PydanticError("One or more element is not a valid area")

        return intervention_area


class VenuesEducationalStatusResponseModel(HttpBodyModel):
    id: int
    name: str


class VenuesEducationalStatusesResponseModel(HttpBodyModel):
    statuses: list[VenuesEducationalStatusResponseModel]
