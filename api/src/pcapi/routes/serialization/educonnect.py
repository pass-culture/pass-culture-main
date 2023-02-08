import datetime

from pcapi.routes.serialization import BaseModel


class EduconnectUserE2ERequest(BaseModel):
    birthDate: datetime.date
    firstName: str
    lastName: str
