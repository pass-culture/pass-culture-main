from pcapi.core.users.models import AccountState
from pcapi.routes.native.v2.serialization.common_models import DeviceInfoV2
from pcapi.routes.serialization import HttpBodyModel
from pcapi.routes.serialization import HttpQueryParamsModel


class SigninRequestV2(HttpQueryParamsModel):
    identifier: str
    password: str
    device_info: DeviceInfoV2
    token: str | None = None


class SigninResponseV2(HttpBodyModel):
    refresh_token: str
    access_token: str
    account_state: AccountState
