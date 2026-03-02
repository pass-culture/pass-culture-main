import datetime
import functools
import typing

import flask
from flask import request

from pcapi import settings
from pcapi.core import token as token_utils
from pcapi.core.users import constants as users_constants
from pcapi.core.users import generator as users_generator
from pcapi.core.users import models as users_models
from pcapi.models import api_errors
from pcapi.models.utils import get_or_404
from pcapi.routes.apis import private_api
from pcapi.routes.backoffice.dev import forms as dev_forms
from pcapi.routes.backoffice.dev.blueprint import create_qf_fraud_check
from pcapi.routes.backoffice.dev.blueprint import create_ubble_fraud_check
from pcapi.routes.backoffice.dev.blueprint import get_token_expiration_timestamp
from pcapi.utils import transaction_manager


API_KEY_HEADER_NAME = "X-API-KEY"


def api_key_required(route_function: typing.Callable) -> typing.Callable:
    @functools.wraps(route_function)
    def wrapper(*args: typing.Any, **kwargs: typing.Any) -> flask.Response:

        if not (request.headers.get(API_KEY_HEADER_NAME) or "").strip():
            raise api_errors.UnauthorizedError(errors={"auth": "API key required"})

        if request.headers[API_KEY_HEADER_NAME] != settings.E2E_API_KEY:
            raise api_errors.ForbiddenError(errors={"auth": "Invalid API key"})

        return route_function(*args, **kwargs)

    return wrapper


@private_api.route("/e2e/account", methods=["POST"])
@transaction_manager.atomic()
@api_key_required
def generate_account() -> tuple[dict, int]:
    form = dev_forms.UserGeneratorForm()

    if not form.validate():
        transaction_manager.mark_transaction_as_invalid()
        return form.errors, 400

    raw_date_created = form.date_created.data
    user_data = users_generator.GenerateUserData(
        age=form.age.data,
        id_provider=users_generator.GeneratedIdProvider[form.id_provider.data],
        step=users_generator.GeneratedSubscriptionStep[form.step.data],
        transition_17_18=form.transition_17_18.data,
        date_created=datetime.datetime(raw_date_created.year, raw_date_created.month, raw_date_created.day),
        postal_code=form.postal_code.data,
    )
    user = users_generator.generate_user(user_data)

    token = token_utils.Token.create(
        token_utils.TokenType.SIGNUP_EMAIL_CONFIRMATION, users_constants.EMAIL_VALIDATION_TOKEN_LIFE_TIME, user.id
    )
    return {
        "id": user.id,
        "email": user.email,
        "access_token": token.encoded_token,
        "expiration_timestamp": get_token_expiration_timestamp(token),
    }, 200


@private_api.route("/e2e/account/<user_id>/ubble", methods=["POST"])
@transaction_manager.atomic()
@api_key_required
def configure_ubble_responses(user_id: int) -> tuple[dict, int]:
    user = get_or_404(users_models.User, user_id)
    form = dev_forms.UbbleConfigurationForm()

    if not form.validate():
        transaction_manager.mark_transaction_as_invalid()
        return form.errors, 400

    create_ubble_fraud_check(user, form)

    return {}, 200


@private_api.route("/e2e/account/<user_id>/quotient_familial", methods=["POST"])
@transaction_manager.atomic()
@api_key_required
def configure_api_quotient_familial_response(user_id: int) -> tuple[dict, int]:
    user = get_or_404(users_models.User, user_id)
    form = dev_forms.QuotientFamilialConfigurationForm()

    if not form.validate():
        transaction_manager.mark_transaction_as_invalid()
        return form.errors, 400

    create_qf_fraud_check(user, form)

    return {}, 200
