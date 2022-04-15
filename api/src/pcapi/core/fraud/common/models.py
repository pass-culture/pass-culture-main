import datetime
import typing

import pydantic
import pydantic.datetime_parse
import pydantic.errors

from pcapi.core.users import models as users_models


class IdentityCheckContent(pydantic.BaseModel):
    def get_registration_datetime(self) -> typing.Optional[datetime.datetime]:
        raise NotImplementedError()

    def get_first_name(self) -> typing.Optional[str]:
        raise NotImplementedError()

    def get_last_name(self) -> typing.Optional[str]:
        raise NotImplementedError()

    def get_married_name(self) -> typing.Optional[str]:
        raise NotImplementedError()

    def get_birth_date(self) -> typing.Optional[datetime.date]:
        raise NotImplementedError()

    def get_id_piece_number(self) -> typing.Optional[str]:
        raise NotImplementedError()

    def get_eligibility_type_at_registration(self) -> typing.Optional[users_models.EligibilityType]:
        from pcapi.core.users import api as users_api

        registration_datetime = self.get_registration_datetime()
        birth_date = self.get_birth_date()

        if registration_datetime is None or birth_date is None:
            return None

        eligibility_at_registration = users_api.get_eligibility_at_date(birth_date, registration_datetime)

        return eligibility_at_registration
