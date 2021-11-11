import datetime
import functools
from typing import Any
from typing import Callable

import flask
import pydantic
import wtforms
import wtforms.validators

from pcapi import settings
from pcapi.connectors.api_demarches_simplifiees import GraphQLApplicationStates
from pcapi.models.api_errors import ApiErrors
from pcapi.models.api_errors import ForbiddenError


def coerce_for_enum(enum):
    def coerce(name):
        if isinstance(name, enum):
            return name
        return enum(name)

    return coerce


class DMSWebhookRequest(pydantic.BaseModel):
    procedure_id: int
    dossier_id: int
    state: GraphQLApplicationStates
    updated_at: datetime.datetime

    @pydantic.validator("updated_at", pre=True)
    def validate_udpated_at(cls, value):  # pylint: disable=no-self-argument
        return datetime.datetime.strptime(value, "%Y-%m-%d %H:%M:%S %z")


def require_dms_token(route_function: Callable[..., Any]):
    @functools.wraps(route_function)
    def validate_dms_token(*args, **kwargs):
        if flask.request.args.get("token") != settings.DMS_WEBHOOK_TOKEN:
            errors = ForbiddenError()
            errors.add_error("token", "Invalid token")
            raise errors

        return route_function(*args, **kwargs)

    return validate_dms_token


class DmsWebhookApplicationForm(wtforms.Form):
    procedure_id = wtforms.IntegerField(validators=[wtforms.validators.InputRequired()])
    dossier_id = wtforms.IntegerField(validators=[wtforms.validators.InputRequired()])
    state = wtforms.SelectField(
        choices=list(GraphQLApplicationStates),
        validators=[
            wtforms.validators.InputRequired(),
            wtforms.validators.AnyOf(values=list(GraphQLApplicationStates)),
        ],
        coerce=coerce_for_enum(GraphQLApplicationStates),
    )
    updated_at = wtforms.DateTimeField(validators=[wtforms.validators.InputRequired()], format="%Y-%m-%d %H:%M:%S %z")


def check_demarches_simplifiees_webhook_payload(payload: dict) -> None:
    try:
        flask.request.form["dossier_id"]
    except:
        errors = ApiErrors()
        errors.add_error("application_id", "Invalid application id")
        raise errors


def check_demarches_simplifiees_webhook_token(token: str) -> None:
    if token != settings.DMS_WEBHOOK_TOKEN:
        errors = ForbiddenError()
        errors.add_error("token", "Invalid token")
        raise errors
