import datetime

from pcapi.core.subscription import schemas as subscription_schemas
from pcapi.core.users import models as users_models


class EduconnectContent(subscription_schemas.IdentityCheckContent):
    birth_date: datetime.date
    civility: users_models.GenderEnum | None = None
    educonnect_id: str
    first_name: str
    ine_hash: str
    last_name: str
    registration_datetime: datetime.datetime | None = None
    school_uai: str | None = None
    student_level: str | None = None

    def get_birth_date(self) -> datetime.date:
        return self.birth_date

    def get_civility(self) -> str | None:
        return self.civility.value if self.civility else None

    def get_first_name(self) -> str:
        return self.first_name

    def get_ine_hash(self) -> str | None:
        return self.ine_hash

    def get_last_name(self) -> str:
        return self.last_name

    def get_registration_datetime(self) -> datetime.datetime | None:
        return self.registration_datetime
