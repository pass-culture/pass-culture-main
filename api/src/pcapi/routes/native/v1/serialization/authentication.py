from enum import Enum

from pcapi.core.users.models import AccountState
from pcapi.routes.native.v1.serialization.account import TrustedDeviceV2
from pcapi.routes.serialization import HttpBodyModel
from pcapi.routes.serialization import HttpQueryParamsModel


class ExtentedTrustedDevice(HttpBodyModel):
    """
    This serializer has all the fields from TrustedDevice/TrustedDeviceV2
    in addition to the last 3 fields (font_scale, resolution and screen_zoom_level)
    that are not used by the backend.
    They are accepted here just to fit with what's the front is sending.
    In future API version we might need to remove them and use TrustedDevice instead.
    """

    device_id: str
    os: str | None = None
    source: str | None = None
    # TODO remove the following fields in future api version
    font_scale: float | None = None
    resolution: str | None = None
    screen_zoom_level: int | None = None

    def to_trusted_device(self) -> TrustedDeviceV2:
        return TrustedDeviceV2(
            device_id=self.device_id,
            os=self.os,
            source=self.source,
        )


class SigninRequest(HttpQueryParamsModel):
    identifier: str
    password: str
    device_info: ExtentedTrustedDevice | None = None
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
    device_info: ExtentedTrustedDevice | None = None


class ResetPasswordResponse(HttpBodyModel):
    access_token: str
    refresh_token: str


class ChangePasswordRequest(HttpQueryParamsModel):
    current_password: str
    new_password: str


class ValidateEmailRequest(HttpQueryParamsModel):
    email_validation_token: str
    device_info: ExtentedTrustedDevice | None = None


class ValidateEmailResponse(HttpBodyModel):
    access_token: str
    refresh_token: str


class OauthStateResponse(HttpBodyModel):
    oauth_state_token: str


class OAuthSigninRequest(HttpQueryParamsModel):
    authorization_code: str
    oauth_state_token: str
    device_info: ExtentedTrustedDevice | None = None
