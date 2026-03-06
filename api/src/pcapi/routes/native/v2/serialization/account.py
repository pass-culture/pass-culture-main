import pydantic

from pcapi.core.users import models as users_models
from pcapi.routes.serialization import HttpBodyModel
from pcapi.routes.serialization import HttpQueryParamsModel


class EmailUpdateStatusResponse(HttpBodyModel):
    new_email: str | None = None
    expired: bool
    status: users_models.EmailHistoryEventTypeEnum
    token: str | None = None
    reset_password_token: str | None = None
    has_recently_reset_password: bool


class EmailChangeConfirmationResponse(HttpBodyModel):
    access_token: str
    refresh_token: str
    new_email_selection_token: str
    reset_password_token: str | None = None


class NewEmailSelectionRequest(HttpQueryParamsModel):
    token: str
    new_email: pydantic.EmailStr
