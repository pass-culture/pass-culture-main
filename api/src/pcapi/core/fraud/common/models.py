import datetime

import pydantic.errors

from pcapi.core.users import models as users_models


class IdentityCheckContent(pydantic.BaseModel):
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

    def get_married_name(self) -> str | None:
        return None

    def get_phone_number(self) -> str | None:
        return None

    def get_postal_code(self) -> str | None:
        return None

    def get_registration_datetime(self) -> datetime.datetime | None:
        return None

    def get_eligibility_type_at_registration(self) -> users_models.EligibilityType | None:
        from pcapi.core.users import api as users_api

        registration_datetime = self.get_registration_datetime()  # pylint: disable=assignment-from-none
        birth_date = self.get_birth_date()

        if registration_datetime is None or birth_date is None:
            return None

        eligibility_at_registration = users_api.get_eligibility_at_date(birth_date, registration_datetime)

        return eligibility_at_registration
