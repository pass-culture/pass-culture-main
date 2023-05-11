from datetime import datetime

import pydantic

from pcapi.routes.serialization import BaseModel
from pcapi.serialization.utils import to_camel


class Cookie(pydantic.ConstrainedStr):
    min_length = 1


class CookiesList(pydantic.ConstrainedList):
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
        extra = pydantic.Extra.forbid
