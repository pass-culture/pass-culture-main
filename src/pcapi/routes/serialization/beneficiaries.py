from pydantic import BaseModel
from pydantic.class_validators import validator

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


class ChangeBeneficiaryEmailRequestBody(BaseModel):
    new_email: str
    password: str


class ChangeBeneficiaryEmailBody(BaseModel):
    token: str
