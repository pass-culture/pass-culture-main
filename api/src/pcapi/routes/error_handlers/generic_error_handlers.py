import json
import logging

from flask import Response
from flask import current_app as app
from flask import request
from sqlalchemy.exc import DatabaseError
from werkzeug import exceptions as werkzeug_exceptions
from werkzeug.exceptions import HTTPException
from werkzeug.exceptions import MethodNotAllowed
from werkzeug.exceptions import NotFound

from pcapi.connectors import sirene
import pcapi.core.finance.exceptions as finance_exceptions
import pcapi.core.offers.exceptions as offers_exceptions
from pcapi.models.api_errors import ApiErrors
from pcapi.models.api_errors import DateTimeCastError
from pcapi.models.api_errors import DecimalCastError
from pcapi.models.api_errors import UnauthorizedError
from pcapi.routes.error_handlers.utils import format_sql_statement_params
from pcapi.utils.image_conversion import ImageRatioError


logger = logging.getLogger(__name__)


HtmlErrorResponse = tuple[str, int]
ApiErrorResponse = tuple[dict | Response, int]


@app.errorhandler(NotFound)
def restize_not_found_route_errors(error: NotFound) -> ApiErrorResponse | HtmlErrorResponse:
    return app.generate_error_response({}, backoffice_template_name="errors/not_found.html"), 404  # type: ignore [attr-defined]


@app.errorhandler(ApiErrors)
def restize_api_errors(error: ApiErrors) -> ApiErrorResponse:
    return app.generate_error_response(error.errors), error.status_code or 400  # type: ignore [attr-defined]


@app.errorhandler(offers_exceptions.TooLateToDeleteStock)
def restize_too_late_to_delete_stock(error: offers_exceptions.TooLateToDeleteStock) -> ApiErrorResponse:
    return app.generate_error_response(error.errors), 400  # type: ignore [attr-defined]


@app.errorhandler(Exception)
def internal_error(error: Exception) -> ApiErrorResponse | HTTPException:
    # pass through HTTP errors
    if isinstance(error, HTTPException):
        return error
    logger.exception("Unexpected error on method=%s url=%s: %s", request.method, request.url, error)
    errors = ApiErrors()
    errors.add_error("global", "Il semble que nous ayons des problèmes techniques :(" + " On répare ça au plus vite.")
    return app.generate_error_response(errors.errors), 500  # type: ignore [attr-defined]


@app.errorhandler(UnauthorizedError)
def unauthorized_error(error: UnauthorizedError) -> Response:
    headers: dict = {}
    if error.www_authenticate:
        headers["WWW-Authenticate"] = error.www_authenticate
        if error.realm:
            headers["WWW-Authenticate"] = '%s realm="%s"' % (headers["WWW-Authenticate"], error.realm)
    return Response(json.dumps(error.errors), 401, headers)


@app.errorhandler(MethodNotAllowed)
def method_not_allowed(error: MethodNotAllowed) -> ApiErrorResponse:
    api_errors = ApiErrors()
    api_errors.add_error("global", "La méthode que vous utilisez n'existe pas sur notre serveur")
    logger.warning("405 %s", error)
    return app.generate_error_response(api_errors.errors), 405  # type: ignore [attr-defined]


@app.errorhandler(DecimalCastError)
def decimal_cast_error(error: DecimalCastError) -> ApiErrorResponse:
    api_errors = ApiErrors()
    logger.warning(json.dumps(error.errors))
    for field in error.errors.keys():
        api_errors.add_error(field, "Saisissez un nombre valide")
    return app.generate_error_response(api_errors.errors), 400  # type: ignore [attr-defined]


@app.errorhandler(DateTimeCastError)
def date_time_cast_error(error: DateTimeCastError) -> ApiErrorResponse:
    api_errors = ApiErrors()
    logger.warning(json.dumps(error.errors))
    for field in error.errors.keys():
        api_errors.add_error(field, "Format de date invalide")
    return app.generate_error_response(api_errors.errors), 400  # type: ignore [attr-defined]


@app.errorhandler(finance_exceptions.DepositTypeAlreadyGrantedException)
def already_activated_exception(error: finance_exceptions.DepositTypeAlreadyGrantedException) -> ApiErrorResponse:
    logger.error(json.dumps(error.errors))
    return app.generate_error_response(error.errors), 405  # type: ignore [attr-defined]


@app.errorhandler(429)
def ratelimit_handler(error: Exception) -> ApiErrorResponse:
    # `pcapi.utils.login_manager` cannot be imported at module-scope,
    # because the application context may not be available and that
    # module needs it.
    from pcapi.utils.login_manager import get_request_authorization

    identifier = None
    try:
        if request.is_json and "identifier" in request.json:  # type: ignore [operator]
            identifier = request.json["identifier"]  # type: ignore [index]
    except (json.JSONDecodeError, werkzeug_exceptions.BadRequest) as e:
        logger.info("Could not extract user identifier from request: %s", e)
    auth = get_request_authorization()
    if auth and auth.username:
        identifier = auth.username
    extra = {
        "method": request.method,
        "identifier": identifier,
        "route": str(request.url_rule),
        "path": request.path,
        "queryParams": request.query_string.decode("UTF-8"),
    }

    logger.warning("Requests ratelimit exceeded on routes url=%s", request.url, extra=extra)
    api_errors = ApiErrors()
    api_errors.add_error("global", "Nombre de tentatives de connexion dépassé, veuillez réessayer dans une minute")
    return app.generate_error_response(api_errors.errors), 429  # type: ignore [attr-defined]


@app.errorhandler(DatabaseError)
def database_error_handler(error: DatabaseError) -> ApiErrorResponse:
    if error.statement:
        try:
            sql_info_extra = {"sql_query": error.statement % format_sql_statement_params(error.params)}
        except Exception:  # pylint: disable=broad-except
            # `format_sql_statement_params()` cannot handle `params`
            # when it's a list, which happens when `executemany()` is
            # used.
            sql_info_extra = {"sql_query": error.statement, "sql_params": error.params}
    else:
        sql_info_extra = {}
    logger.info(
        "Database error with the following query on method=%s url=%s. 🚨🚨🚨🚨🚨 BEFORE COPYING THE QUERY MAKE SURE THERE IS NO SQL INJECTION 🚨🚨🚨🚨🚨🚨",
        request.method,
        request.url,
        extra=sql_info_extra,
    )
    logger.exception("Unexpected database error on method=%s url=%s: %s", request.method, request.url, error)
    errors = ApiErrors()
    errors.add_error("global", "Il semble que nous ayons des problèmes techniques :(" + " On répare ça au plus vite.")
    return app.generate_error_response(errors.errors), 500  # type: ignore [attr-defined]


@app.errorhandler(ImageRatioError)
def handle_ratio_error(error: ImageRatioError) -> ApiErrorResponse:
    logger.info("Image ratio error: %s", error)
    return app.generate_error_response({"code": "BAD_IMAGE_RATIO", "extra": str(error)}), 400  # type: ignore [attr-defined]


@app.errorhandler(sirene.UnknownEntityException)
def handle_unknown_entity_exception(error: sirene.UnknownEntityException) -> ApiErrorResponse:
    msg = "Le SIREN n’existe pas."
    err = {"global": [msg]}
    return app.generate_error_response(err), 400  # type: ignore [attr-defined]


@app.errorhandler(sirene.InvalidFormatException)
def handle_sirene_invalid_format_exception(error: sirene.InvalidFormatException) -> ApiErrorResponse:
    msg = "Le format de ce SIREN ou SIRET est incorrect."
    err = {"global": [msg]}
    return app.generate_error_response(err), 400  # type: ignore [attr-defined]


@app.errorhandler(sirene.NonPublicDataException)
def handle_sirene_non_public_data_exception(error: sirene.NonPublicDataException) -> ApiErrorResponse:
    msg = "Les informations relatives à ce SIREN ou SIRET ne sont pas accessibles."
    err = {"global": [msg]}
    return app.generate_error_response(err), 400  # type: ignore [attr-defined]
