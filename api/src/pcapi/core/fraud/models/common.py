import datetime
import typing

import pydantic


class SubscriptionContentType(pydantic.BaseModel):
    def get_registration_datetime(self) -> typing.Optional[datetime.datetime]:
        raise NotImplementedError()

    def get_birth_date(self) -> typing.Optional[datetime.date]:
        raise NotImplementedError()
