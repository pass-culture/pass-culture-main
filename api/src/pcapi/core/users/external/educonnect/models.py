from dataclasses import dataclass
import datetime
from typing import Optional


@dataclass
class EduconnectUser:
    birth_date: datetime.date
    connection_datetime: datetime.datetime
    educonnect_id: str
    first_name: str
    ine_hash: str
    last_name: str
    logout_url: str
    saml_request_id: str
    student_level: Optional[str]
