import datetime
import typing

import pydantic

from pcapi.core.users.models import EligibilityType


class IdentityCheckContent(pydantic.BaseModel):
    def get_registration_datetime(self) -> typing.Optional[datetime.datetime]:
        raise NotImplementedError()

    def get_first_name(self) -> typing.Optional[str]:
        raise NotImplementedError()

    def get_last_name(self) -> typing.Optional[str]:
        raise NotImplementedError()

    def get_birth_date(self) -> typing.Optional[datetime.date]:
        raise NotImplementedError()

    def get_id_piece_number(self) -> typing.Optional[str]:
        raise NotImplementedError()

    def get_eligibility_type(self) -> typing.Optional[EligibilityType]:
        from pcapi.core.users import api as users_api

        registration_datetime = self.get_registration_datetime()
        birth_date = self.get_birth_date()

        if registration_datetime is None or birth_date is None:
            return None

        eligibility_at_registration = users_api.get_eligibility_at_date(birth_date, registration_datetime)
        eligibility_today = users_api.get_eligibility_at_date(birth_date, datetime.datetime.now())

        # When a user turns 18, his underage credit expires.
        # If he turned 18 between registration and today, we consider the application as coming from a 18 years old user
        if eligibility_today == EligibilityType.AGE18 and eligibility_at_registration == EligibilityType.UNDERAGE:
            return EligibilityType.AGE18

        return eligibility_at_registration
