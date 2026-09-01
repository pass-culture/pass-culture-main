from typing import Annotated

import pydantic as pydantic_v2
from pydantic import BeforeValidator

from pcapi.core.offerers import models


def parse_venue_activity(activity: str | models.Activity) -> models.Activity:
    if isinstance(activity, str):
        return models.Activity[activity]
    return activity


class Venue(pydantic_v2.BaseModel):
    id: int
    activity: Annotated[models.Activity, BeforeValidator(parse_venue_activity)]
    has_ticketing: bool = False


class Product(pydantic_v2.BaseModel):
    id: int


class ProviderData(pydantic_v2.BaseModel):
    id_at_provider: str
    provider_id: int
