import datetime

from pcapi.routes.serialization import HttpBodyModel


class EduconnectUserE2ERequest(HttpBodyModel):
    birth_date: datetime.date
    first_name: str
    last_name: str
