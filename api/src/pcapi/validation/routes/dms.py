import datetime
import functools
from typing import Any
from typing import Callable

import flask
import pydantic.v1 as pydantic_v1

from pcapi import settings
from pcapi.connectors.dms import models as dms_models
from pcapi.models.api_errors import ForbiddenError
from pcapi.models.api_errors import UnauthorizedError


class DMSWebhookRequest(pydantic_v1.BaseModel):
    procedure_id: int
    dossier_id: int
    state: dms_models.GraphQLApplicationStates
    updated_at: datetime.datetime

    @pydantic_v1.validator("updated_at", pre=True)
    def validate_udpated_at(cls, value: str) -> datetime.datetime:
        return datetime.datetime.strptime(value, "%Y-%m-%d %H:%M:%S %z")


def require_dms_token(route_function: Callable[..., Any]) -> Callable:
    @functools.wraps(route_function)
    def validate_dms_token(*args: Any, **kwargs: Any) -> flask.Response:
        token = flask.request.args.get("token")
        if not token:
            raise UnauthorizedError()

        if token != settings.DMS_WEBHOOK_TOKEN:
            errors = ForbiddenError()
            errors.add_error("token", "Invalid token")
            raise errors

        return route_function(*args, **kwargs)

    return validate_dms_token
