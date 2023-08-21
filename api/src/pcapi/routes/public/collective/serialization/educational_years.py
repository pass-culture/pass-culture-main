from datetime import datetime

from pcapi.routes.serialization import BaseModel


class EducationalYearModel(BaseModel):
    adageId: str
    beginningDate: datetime
    expirationDate: datetime

    class Config:
        orm_mode = True
