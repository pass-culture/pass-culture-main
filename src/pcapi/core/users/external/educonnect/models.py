from dataclasses import dataclass
import datetime
from typing import Optional


@dataclass
class EduconnectUser:
    connection_datetime: datetime.datetime
    birth_date: datetime.date
    educonnect_id: str
    ine_hash: str
    first_name: str
    last_name: str
    logout_url: str
    saml_request_id: str
    student_level: Optional[str]
