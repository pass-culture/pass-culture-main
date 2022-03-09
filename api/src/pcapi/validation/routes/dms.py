import datetime
import functools
from typing import Any
from typing import Callable

import flask
import pydantic

from pcapi import settings
from pcapi.connectors.dms import models as dms_models
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
    state: dms_models.GraphQLApplicationStates
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


class BankInformationDmsFormModel(pydantic.BaseModel):
    dossier_id: str
    procedure_id: str


class BankInformationDmsResponseModel(pydantic.BaseModel):
    pass
