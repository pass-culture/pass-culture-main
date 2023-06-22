from pcapi.routes.serialization import BaseModel


class RedactorPreferences(BaseModel):
    feedback_form_closed: bool

    class Config:
        extra = "forbid"
