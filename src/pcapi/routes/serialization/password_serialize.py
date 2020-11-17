from typing import Optional

from pydantic.class_validators import validator
from pydantic.main import BaseModel

from pcapi.models.api_errors import ApiErrors


class ResetPasswordBodyModel(BaseModel):
    email: str
    token: str

    @validator("email")
    def validate_email_not_empty(cls, email: str) -> Optional[str]:  # typing: ignore # pylint: disable=no-self-argument
        if not email or email.isspace():
            errors = ApiErrors()
            errors.add_error("email", "L'email renseigné est vide")
            raise errors

        return email
