from pcapi.core.users.models import AccountState
from pcapi.routes.serialization import BaseModel
from pcapi.serialization.utils import to_camel


class SigninRequest(BaseModel):
    identifier: str
    password: str


class SigninResponse(BaseModel):
    refresh_token: str
    access_token: str
    account_state: AccountState

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True


class RefreshResponse(BaseModel):
    access_token: str

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True


class RequestPasswordResetRequest(BaseModel):
    email: str
    token: str | None = None


class ResetPasswordRequest(BaseModel):
    reset_password_token: str
    new_password: str

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

    class Config:
        alias_generator = to_camel


class ValidateEmailRequest(BaseModel):
    email_validation_token: str

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True


class ValidateEmailResponse(BaseModel):
    access_token: str
    refresh_token: str

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True
