from datetime import datetime
from typing import Optional

import pydantic

from pcapi.routes.serialization import BaseModel
from pcapi.serialization.utils import to_camel


Cookie = pydantic.constr(min_length=1)


CookiesList = pydantic.conlist(item_type=Cookie, unique_items=True)

UUID = str


class Consent(BaseModel):
    mandatory: CookiesList  # type: ignore[valid-type]
    accepted: CookiesList  # type: ignore[valid-type]
    refused: CookiesList  # type: ignore[valid-type]


class CookieConsentRequest(BaseModel):
    consent: Consent
    choice_datetime: datetime
    device_id: UUID

    user_id: Optional[int]

    class Config:
        alias_generator = to_camel
        extra = pydantic.Extra.forbid
