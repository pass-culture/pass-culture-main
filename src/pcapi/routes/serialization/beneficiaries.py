from pydantic import BaseModel  # pylint: disable=no-name-in-module
from pydantic.class_validators import validator  # pylint: disable=no-name-in-module

from pcapi.models.api_errors import ApiErrors


class VerifyIdCheckLicenceRequest(BaseModel):
    token: str

    @validator("token")
    def validate_token_not_empty(cls, token: str) -> str:  # typing: ignore # pylint: disable=no-self-argument
        if token == "null":
            raise ApiErrors({"token": "Empty token"})
        return token


class VerifyIdCheckLicenceResponse(BaseModel):
    pass


class ApplicationUpdateRequest(BaseModel):
    id: str


class ApplicationUpdateResponse(BaseModel):
    pass
