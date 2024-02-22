from pcapi.routes.serialization import ConfiguredBaseModel


class EmailChangeConfirmationResponse(ConfiguredBaseModel):
    access_token: str
    refresh_token: str
    new_email_selection_token: str
