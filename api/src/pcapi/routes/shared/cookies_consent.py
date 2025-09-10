from datetime import datetime

import pydantic.v1 as pydantic_v1

from pcapi.routes.serialization import BaseModel
from pcapi.routes.serialization import to_camel


class Cookie(pydantic_v1.ConstrainedStr):
    min_length = 1


class CookiesList(pydantic_v1.ConstrainedList):
    item_type = Cookie
    __args__ = (Cookie,)  # required by pydantic
    unique_items = True


UUID = str


class Consent(BaseModel):
    mandatory: CookiesList
    accepted: CookiesList
    refused: CookiesList


class CookieConsentRequest(BaseModel):
    consent: Consent
    choice_datetime: datetime
    device_id: UUID

    user_id: int | None

    class Config:
        alias_generator = to_camel
        extra = pydantic_v1.Extra.forbid
