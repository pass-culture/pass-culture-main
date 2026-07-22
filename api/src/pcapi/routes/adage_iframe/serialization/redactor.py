import pydantic as pydantic_v2

from pcapi.routes.serialization import BaseModel
from pcapi.routes.serialization import HttpBodyModel


class RedactorPreferences(BaseModel):
    feedback_form_closed: bool | None
    broadcast_help_closed: bool | None

    class Config:
        extra = "forbid"


# when RedactorPreferences is not used anymore, check if we can remove alias_generator=None
class RedactorPreferencesV2(HttpBodyModel):
    feedback_form_closed: bool | None = None
    broadcast_help_closed: bool | None = None

    model_config = pydantic_v2.ConfigDict(
        alias_generator=None,
    )
