import datetime
import typing

import flask

from pcapi import settings


def _format_statement_value(value: typing.Any) -> typing.Any:
    if isinstance(value, int):
        return value

    if isinstance(value, (str, datetime.date, datetime.datetime, datetime.timedelta)):
        # Add quotes to make psql recognize the value as a string
        return f"'{str(value)}'"

    if isinstance(value, list):
        formatted_list = []
        for x in value:
            formatted_list.append(_format_statement_value(x))
        return formatted_list

    return str(value)


def format_sql_statement_params(params: dict | None) -> dict | None:
    if params is None:
        return None
    return {key: _format_statement_value(value) for key, value in params.items()}


def generate_error_response(errors: dict, backoffice_template_name: str = "errors/generic.html") -> flask.Response:
    app_name = flask.current_app.config["NAME"]

    match app_name:
        case settings.BACKEND_APP_NAME:
            return _generate_error_response_backend(errors)

        case settings.BACKOFFICE_APP_NAME:
            return _generate_error_response_backoffice(errors, backoffice_template_name)

        case _:
            raise ValueError("Unknown current app name")


def _generate_error_response_backend(errors: dict) -> flask.Response:
    return flask.jsonify(errors)


def _format_response_error_messages(errors: dict) -> list[str]:
    """
    Format unhandled errors for htmx requests
    """
    lines = []
    for error_key, error_details in errors.items():
        for error_detail in error_details:
            lines.append(f"[{error_key}] {error_detail}")
    return lines


def _generate_error_response_backoffice(errors: dict, backoffice_template_name: str) -> flask.Response:
    from pcapi.routes.backoffice.utils.request import is_request_from_htmx
    from pcapi.routes.backoffice.utils.static import get_hashes

    # In case of a request coming from htmx, display errors as flash messages
    if is_request_from_htmx():
        for error_line in _format_response_error_messages(errors):
            flask.flash(error_line, "danger")
        return flask.make_response()

    return flask.make_response(
        flask.render_template(
            backoffice_template_name,
            errors=errors,
            static_hashes=get_hashes(),
        )
    )
