from pcapi.routes.serialization import BaseModel
from pydantic import ConfigDict


class RedactorPreferences(BaseModel):
    feedback_form_closed: bool | None
    broadcast_help_closed: bool | None
    model_config = ConfigDict(extra="forbid")
