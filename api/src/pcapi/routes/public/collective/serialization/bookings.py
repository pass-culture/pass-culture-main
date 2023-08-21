from datetime import datetime

from pcapi.core.educational import models
from pcapi.routes.serialization import BaseModel

from . import educational_years


class CollectiveBookingResponseModel(BaseModel):
    id: int
    status: models.CollectiveBookingStatus
    dateUsed: datetime | None
    cancellationLimitDate: datetime | None
    dateCreated: datetime
    confirmationDate: datetime | None
    educationalYear: educational_years.EducationalYearModel
    venueId: int

    class Config:
        orm_mode = True
