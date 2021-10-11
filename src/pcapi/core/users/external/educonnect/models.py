from dataclasses import dataclass
import datetime


@dataclass
class EduconnectUser:
    connection_datetime: datetime.datetime
    birth_date: datetime.date
    educonnect_id: str
    first_name: str
    last_name: str
    saml_request_id: str
    student_level: str
