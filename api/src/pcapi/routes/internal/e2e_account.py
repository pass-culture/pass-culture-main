import contextlib
import datetime

import pydantic.v1 as pydantic_v1

from pcapi.core import token as token_utils
from pcapi.core.mails.transactional.users.email_address_change_confirmation import get_email_confirmation_email_data
from pcapi.core.users import constants
from pcapi.core.users import generator as users_generator
from pcapi.routes.native import blueprint
from pcapi.routes.serialization import ConfiguredBaseModel
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils import transaction_manager


class AccountGenerationRequest(ConfiguredBaseModel):
    age: int
    id_provider: users_generator.GeneratedIdProvider
    step: users_generator.GeneratedSubscriptionStep
    date_created: datetime.datetime
    transition1718: bool
    postal_code: str

    @pydantic_v1.validator("id_provider", pre=True)
    def parse_id_provider(cls, id_provider: str | None) -> users_generator.GeneratedIdProvider | None:
        if not id_provider:
            return None
        with contextlib.suppress(KeyError):
            return users_generator.GeneratedIdProvider[id_provider.upper()]
        return None

    class Config:
        use_enum_values = False


class AccountGenerationResponse(ConfiguredBaseModel):
    confirmation_link: str


@blueprint.native_route("/account/e2e", methods=["POST"])
@spectree_serialize(on_success_status=200, api=blueprint.api, on_error_statuses=[400])
@transaction_manager.atomic()
def generate_account(body: AccountGenerationRequest) -> AccountGenerationResponse:
    user_data = users_generator.GenerateUserData(
        age=body.age,
        id_provider=body.id_provider,
        step=body.step,
        transition_17_18=body.transition1718,
        date_created=body.date_created,
        postal_code=body.postal_code,
    )
    user = users_generator.generate_user(user_data)

    email_validation_token = token_utils.Token.create(
        token_utils.TokenType.SIGNUP_EMAIL_CONFIRMATION,
        constants.EMAIL_VALIDATION_TOKEN_LIFE_TIME,
        user.id,
    )
    email_data = get_email_confirmation_email_data(user.email, email_validation_token)
    return AccountGenerationResponse(confirmation_link=email_data.params["CONFIRMATION_LINK"])
