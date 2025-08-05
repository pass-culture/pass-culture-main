from pcapi.core import token as token_utils
from pcapi.core.users import constants
from pcapi.core.users import factories as users_factories
from pcapi.utils.urls import generate_firebase_dynamic_link

from .blueprint import e2e_app_blueprint


@e2e_app_blueprint.route("/create_beneficiary", methods=["GET"])
def create_beneficiary():
    beneficiary = users_factories.BeneficiaryFactory.create()
    token = token_utils.Token.create(
        token_utils.TokenType.SIGNUP_EMAIL_CONFIRMATION,
        constants.EMAIL_VALIDATION_TOKEN_LIFE_TIME,
        beneficiary.id,
    )
    expiration_timestamp = int(token.get_expiration_date_from_token().timestamp())
    email_confirmation_link = generate_firebase_dynamic_link(
        path="signup-confirmation",
        params={"token": token.encoded_token, "expiration_timestamp": expiration_timestamp, "email": beneficiary.email},
    )
    return {"userId": beneficiary.id, "email": beneficiary.email, "activationLink": email_confirmation_link}
