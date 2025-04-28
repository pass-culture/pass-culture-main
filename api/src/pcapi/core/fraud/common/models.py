import datetime

import pydantic.v1 as pydantic_v1

from pcapi.core.users import models as users_models
from pcapi.utils import postal_code as postal_code_utils


class IdentityCheckContent(pydantic_v1.BaseModel):
    def get_birth_date(self) -> datetime.date | None:
        raise NotImplementedError()

    def get_first_name(self) -> str | None:
        raise NotImplementedError()

    def get_last_name(self) -> str | None:
        raise NotImplementedError()

    def get_activity(self) -> str | None:
        return None

    def get_address(self) -> str | None:
        return None

    def get_civility(self) -> str | None:
        return None

    def get_city(self) -> str | None:
        return None

    def get_id_piece_number(self) -> str | None:
        return None

    def get_ine_hash(self) -> str | None:
        return None

    def get_latest_modification_datetime(self) -> datetime.datetime | None:
        return None

    def get_married_name(self) -> str | None:
        return None

    def get_phone_number(self) -> str | None:
        return None

    def get_postal_code(self) -> str | None:
        return None

    def get_registration_datetime(self) -> datetime.datetime | None:
        return None

    def get_eligibility_type_at_registration(self) -> users_models.EligibilityType | None:
        from pcapi.core.users import eligibility_api

        registration_datetime = self.get_registration_datetime()
        birth_date = self.get_birth_date()

        if registration_datetime is None or birth_date is None:
            return None

        postal_code = self.get_postal_code()
        department = postal_code_utils.PostalCode(postal_code).get_departement_code() if postal_code else None
        eligibility_at_registration = eligibility_api.get_eligibility_at_date(
            birth_date, registration_datetime, department
        )

        return eligibility_at_registration
