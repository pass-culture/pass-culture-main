from pydantic.class_validators import validator
from pydantic.main import BaseModel

from pcapi.models.api_errors import ApiErrors
from pcapi.serialization.utils import validate_not_empty_string_when_provided


class ResetPasswordBodyModel(BaseModel):
    email: str
    token: str

    @validator("email")
    def validate_email_not_empty(cls, email: str) -> str | None:  # typing: ignore # pylint: disable=no-self-argument
        if not email or email.isspace():
            errors = ApiErrors()
            errors.add_error("email", "L'email renseigné est vide")
            raise errors

        return email


class ChangePasswordBodyModel(BaseModel):
    oldPassword: str
    newPassword: str
    newConfirmationPassword: str

    _validate_oldPassword = validate_not_empty_string_when_provided("oldPassword")
    _validate_newPassword = validate_not_empty_string_when_provided("newPassword")
    _validate_newConfirmationPassword = validate_not_empty_string_when_provided("newConfirmationPassword")


class NewPasswordBodyModel(BaseModel):
    token: str
    newPassword: str

    _validate_token = validate_not_empty_string_when_provided("token")
    _validate_newPassword = validate_not_empty_string_when_provided("newPassword")
