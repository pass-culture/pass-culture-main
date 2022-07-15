from dataclasses import dataclass
import datetime


@dataclass
class EduconnectUser:
    birth_date: datetime.date
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
