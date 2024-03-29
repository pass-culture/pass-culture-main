from pcapi.routes.serialization import BaseModel


class RedactorPreferences(BaseModel):
    feedback_form_closed: bool | None
    broadcast_help_closed: bool | None

    class Config:
        extra = "forbid"
