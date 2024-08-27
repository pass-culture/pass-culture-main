from flask import current_app as app

from pcapi import settings
from pcapi.models.api_errors import ApiErrors
from pcapi.routes.error_handlers.generic_error_handlers import ApiErrorResponse


class UnauthorizedEnvironment(Exception):
    pass


@app.errorhandler(UnauthorizedEnvironment)
def handle_unauthorized_env(_: UnauthorizedEnvironment) -> ApiErrorResponse:
    msg = f"unauthorized action from {settings.ENV}"
    error = ApiErrors(status_code=403, errors={"msg": msg})

    return app.generate_error_response(error.errors), error.status_code
