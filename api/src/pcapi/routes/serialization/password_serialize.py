from pydantic.v1.class_validators import validator
from pydantic.v1.main import BaseModel

from pcapi.models.api_errors import ApiErrors
from pcapi.serialization.utils import validate_not_empty_string_when_provided
from pydantic import field_validator


class ResetPasswordBodyModel(BaseModel):
    email: str
    token: str

    @field_validator("email")
    @classmethod
    def validate_email_not_empty(cls, email: str) -> str | None:  # typing: ignore
        if not email or email.isspace():
            errors = ApiErrors()
            errors.add_error("email", "L'email renseigné est vide")
            raise errors

        return email


class NewPasswordBodyModel(BaseModel):
    token: str
    newPassword: str

    _validate_token = validate_not_empty_string_when_provided("token")
    _validate_newPassword = validate_not_empty_string_when_provided("newPassword")
