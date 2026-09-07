import pydantic

from pcapi.routes.serialization import HttpBodyModel


class RedactorPreferences(HttpBodyModel):
    feedback_form_closed: bool | None = None
    broadcast_help_closed: bool | None = None

    model_config = pydantic.ConfigDict(
        alias_generator=None,
    )
