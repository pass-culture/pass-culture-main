from dataclasses import dataclass
import datetime

from pcapi.core.users import models as users_models


@dataclass
class EduconnectUser:
    birth_date: datetime.date
    civility: users_models.GenderEnum | None
    connection_datetime: datetime.datetime | None
    educonnect_id: str
    first_name: str
    ine_hash: str
    last_name: str
    logout_url: str
    saml_request_id: str
    school_uai: str | None
    student_level: str | None
    user_type: str | None
