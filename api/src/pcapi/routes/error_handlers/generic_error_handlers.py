import logging
from typing import Union

from flask import Response
from flask import current_app as app
from flask import jsonify
from flask import request
import simplejson as json
from sqlalchemy.exc import DatabaseError
from werkzeug.exceptions import HTTPException
from werkzeug.exceptions import MethodNotAllowed
from werkzeug.exceptions import NotFound

import pcapi.core.offers.exceptions as offers_exceptions
from pcapi.core.payments.exceptions import DepositTypeAlreadyGrantedException
from pcapi.models.api_errors import ApiErrors
from pcapi.models.api_errors import DateTimeCastError
from pcapi.models.api_errors import DecimalCastError
from pcapi.models.api_errors import UnauthorizedError
from pcapi.routes.error_handlers.utils import format_sql_statement_params
from pcapi.utils.human_ids import NonDehumanizableId


logger = logging.getLogger(__name__)


@app.errorhandler(NotFound)
def restize_not_found_route_errors(error: NotFound) -> tuple[dict, int]:
    return {}, 404


@app.errorhandler(ApiErrors)
def restize_api_errors(error: ApiErrors) -> tuple[dict, int]:
    return jsonify(error.errors), error.status_code or 400


@app.errorhandler(offers_exceptions.TooLateToDeleteStock)
def restize_too_late_to_delete_stock(error: offers_exceptions.TooLateToDeleteStock) -> tuple[dict, int]:
    return jsonify(error.errors), 400


@app.errorhandler(Exception)
def internal_error(error: Exception) -> Union[tuple[dict, int], HTTPException]:
    # pass through HTTP errors
    if isinstance(error, HTTPException):
        return error
    logger.exception("Unexpected error on method=%s url=%s: %s", request.method, request.url, error)
    errors = ApiErrors()
    errors.add_error("global", "Il semble que nous ayons des problèmes techniques :(" + " On répare ça au plus vite.")
    return jsonify(errors.errors), 500


@app.errorhandler(UnauthorizedError)
def unauthorized_error(error: UnauthorizedError) -> Response:
    headers: dict = {}
    if error.www_authenticate:
        headers["WWW-Authenticate"] = error.www_authenticate
        if error.realm:
            headers["WWW-Authenticate"] = '%s realm="%s"' % (headers["WWW-Authenticate"], error.realm)
    return Response(json.dumps(error.errors), 401, headers)


@app.errorhandler(MethodNotAllowed)
def method_not_allowed(error: MethodNotAllowed) -> tuple[dict, int]:
    api_errors = ApiErrors()
    api_errors.add_error("global", "La méthode que vous utilisez n'existe pas sur notre serveur")
    logger.warning("405 %s", error)
    return jsonify(api_errors.errors), 405


@app.errorhandler(NonDehumanizableId)
def invalid_id_for_dehumanize_error(error: NonDehumanizableId) -> tuple[dict, int]:
    api_errors = ApiErrors()
    api_errors.add_error("global", "La page que vous recherchez n'existe pas")
    logger.warning("404 %s", error)
    return jsonify(api_errors.errors), 404


@app.errorhandler(DecimalCastError)
def decimal_cast_error(error: DecimalCastError) -> tuple[dict, int]:
    api_errors = ApiErrors()
    logger.warning(json.dumps(error.errors))
    for field in error.errors.keys():
        api_errors.add_error(field, "Saisissez un nombre valide")
    return jsonify(api_errors.errors), 400


@app.errorhandler(DateTimeCastError)
def date_time_cast_error(error: DateTimeCastError) -> tuple[dict, int]:
    api_errors = ApiErrors()
    logger.warning(json.dumps(error.errors))
    for field in error.errors.keys():
        api_errors.add_error(field, "Format de date invalide")
    return jsonify(api_errors.errors), 400


@app.errorhandler(DepositTypeAlreadyGrantedException)
def already_activated_exception(error: DepositTypeAlreadyGrantedException) -> tuple[dict, int]:
    logger.error(json.dumps(error.errors))
    return jsonify(error.errors), 405


@app.errorhandler(429)
def ratelimit_handler(error: Exception) -> tuple[dict, int]:
    # `pcapi.utis.login_manager` cannot be imported at module-scope,
    # because the application context may not be available and that
    # module needs it.
    from pcapi.utils.login_manager import get_request_authorization

    identifier = None
    try:
        if request.is_json and "identifier" in request.json:
            identifier = request.json["identifier"]
    except json.JSONDecodeError as e:
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
    return jsonify(api_errors.errors), 429


@app.errorhandler(DatabaseError)
def database_error_handler(error: DatabaseError) -> tuple[dict, int]:
    logger.info(
        "Database error with the following query on method=%s url=%s. 🚨🚨🚨🚨🚨 BEFORE COPYING THE QUERY MAKE SURE THERE IS NO SQL INJECTION 🚨🚨🚨🚨🚨🚨",
        request.method,
        request.url,
        extra={
            "sql_query": error.statement % format_sql_statement_params(error.params)
            if error.statement is not None
            else None
        },
    )
    logger.exception("Unexpected database error on method=%s url=%s: %s", request.method, request.url, error)
    errors = ApiErrors()
    errors.add_error("global", "Il semble que nous ayons des problèmes techniques :(" + " On répare ça au plus vite.")
    return jsonify(errors.errors), 500
