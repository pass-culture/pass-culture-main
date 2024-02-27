from pydantic import v1 as pydantic_v1

from pcapi.core.users import models as users_models
from pcapi.routes.serialization import ConfiguredBaseModel


class EmailUpdateStatusResponse(ConfiguredBaseModel):
    new_email: str | None
    expired: bool
    status: users_models.EmailHistoryEventTypeEnum
    token: str | None


class EmailChangeConfirmationResponse(ConfiguredBaseModel):
    access_token: str
    refresh_token: str
    new_email_selection_token: str


class NewEmailSelectionRequest(ConfiguredBaseModel):
    token: str
    new_email: pydantic_v1.EmailStr
