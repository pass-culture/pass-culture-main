from pcapi.core.users.account import TrustedDevice
from pcapi.core.users.models import AccountState
from pcapi.routes.serialization import ConfiguredBaseModel


class SigninRequest(ConfiguredBaseModel):
    identifier: str
    password: str
    device_info: TrustedDevice | None = None
    token: str | None = None


class SigninResponse(ConfiguredBaseModel):
    refresh_token: str
    access_token: str
    account_state: AccountState


class RefreshResponse(ConfiguredBaseModel):
    access_token: str


class RequestPasswordResetRequest(ConfiguredBaseModel):
    email: str
    token: str | None = None


class ResetPasswordRequest(ConfiguredBaseModel):
    reset_password_token: str
    new_password: str
    device_info: TrustedDevice | None = None


class ResetPasswordResponse(ConfiguredBaseModel):
    access_token: str
    refresh_token: str


class ChangePasswordRequest(ConfiguredBaseModel):
    current_password: str
    new_password: str


class ValidateEmailRequest(ConfiguredBaseModel):
    email_validation_token: str
    device_info: TrustedDevice | None = None


class ValidateEmailResponse(ConfiguredBaseModel):
    access_token: str
    refresh_token: str


class OauthStateResponse(ConfiguredBaseModel):
    oauth_state_token: str


class GoogleSigninRequest(ConfiguredBaseModel):
    authorization_code: str
    oauth_state_token: str
    device_info: TrustedDevice | None = None
