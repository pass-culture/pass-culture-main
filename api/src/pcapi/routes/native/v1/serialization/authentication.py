from enum import Enum

from pcapi.core.users.models import AccountState
from pcapi.routes.native.v1.serialization.account import TrustedDeviceV2
from pcapi.routes.serialization import HttpBodyModel
from pcapi.routes.serialization import HttpQueryParamsModel


class SigninRequest(HttpQueryParamsModel):
    identifier: str
    password: str
    device_info: TrustedDeviceV2 | None = None
    token: str | None = None


class SigninResponse(HttpBodyModel):
    refresh_token: str
    access_token: str
    account_state: AccountState


class SSOProvider(Enum):
    APPLE = "apple"
    GOOGLE = "google"


class RefreshResponse(HttpBodyModel):
    access_token: str


class RequestPasswordResetRequest(HttpQueryParamsModel):
    email: str
    token: str | None = None


class ResetPasswordRequest(HttpQueryParamsModel):
    reset_password_token: str
    new_password: str
    device_info: TrustedDeviceV2 | None = None


class ResetPasswordResponse(HttpBodyModel):
    access_token: str
    refresh_token: str


class ChangePasswordRequest(HttpQueryParamsModel):
    current_password: str
    new_password: str


class ValidateEmailRequest(HttpQueryParamsModel):
    email_validation_token: str
    device_info: TrustedDeviceV2 | None = None


class ValidateEmailResponse(HttpBodyModel):
    access_token: str
    refresh_token: str


class OauthStateResponse(HttpBodyModel):
    oauth_state_token: str


class OAuthSigninRequest(HttpQueryParamsModel):
    authorization_code: str
    oauth_state_token: str
    device_info: TrustedDeviceV2 | None = None
