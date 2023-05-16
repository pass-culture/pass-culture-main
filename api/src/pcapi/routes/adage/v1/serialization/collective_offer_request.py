from datetime import date

from pydantic.fields import Field

from pcapi.routes.adage.v1.serialization.config import AdageBaseResponseModel


class CollectiveOfferRequestResponse(AdageBaseResponseModel):
    phoneNumber: str | None
    requestedDate: date | None
    totalStudents: int | None
    totalTeachers: int | None
    comment: str = Field(description="Commentaire à mettre")
