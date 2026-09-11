from pcapi.core.users.models import AccountState
from pcapi.routes.serialization import HttpBodyModel
from pcapi.routes.serialization import HttpQueryParamsModel


class MfaOfferV3(HttpBodyModel):
    type: str
    endpoint: str


class DeviceInfoV3(HttpBodyModel):
    device_id: str
    os: str | None = None
    source: str | None = None


class SigninRequestV3(HttpQueryParamsModel):
    identifier: str
    password: str
    device_info: DeviceInfoV3
    token: str | None = None


class SigninResponseV3(HttpBodyModel):
    mfa_offers: list[MfaOfferV3]
    expiration: int


class OtpChallengeV3(HttpBodyModel):
    new_email_sent: bool
    expiration: int
    renewal_email: int
    retry_left: int
    char_count: int
    response_endpoint: str


class OtpRequestV3(HttpQueryParamsModel):
    response: str


class UserAuthenticatedV3(HttpBodyModel):
    refresh_token: str
    access_token: str
    account_state: AccountState


class OtpResponseV3(HttpBodyModel):
    expiration: int
    renewal_email: int
    char_count: int
    retry_left: int
    response_endpoint: str | None
    session_tokens: UserAuthenticatedV3 | None
