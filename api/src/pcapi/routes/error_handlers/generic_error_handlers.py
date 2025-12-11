import json
import logging

from flask import Response
from flask import current_app as app
from flask import flash
from flask import request
from flask import session
from sqlalchemy.exc import DatabaseError
from werkzeug import exceptions as werkzeug_exceptions
from werkzeug.exceptions import HTTPException
from werkzeug.exceptions import MethodNotAllowed
from werkzeug.exceptions import NotFound

import pcapi.core.finance.exceptions as finance_exceptions
from pcapi.connectors.entreprise import exceptions as sirene_exceptions
from pcapi.core import core_exception
from pcapi.core.offers.exceptions import OfferNotFound
from pcapi.models.api_errors import ApiErrors
from pcapi.models.api_errors import DateTimeCastError
from pcapi.models.api_errors import DecimalCastError
from pcapi.models.api_errors import UnauthorizedError
from pcapi.routes.error_handlers.utils import format_sql_statement_params
from pcapi.utils.image_conversion import ImageRatioError
from pcapi.utils.transaction_manager import mark_transaction_as_invalid


logger = logging.getLogger(__name__)


HtmlErrorResponse = tuple[str, int]
ApiErrorResponse = tuple[dict | Response, int]


@app.errorhandler(NotFound)
def restize_not_found_route_errors(error: NotFound) -> ApiErrorResponse | HtmlErrorResponse:
    from pcapi.routes.backoffice import utils

    if utils.is_request_from_htmx():
        flashes = session.get("_flashes")
        if not flashes:
            flash("Objet non trouvé !", "warning")
        return "", 404

    return app.generate_error_response({}, backoffice_template_name="errors/not_found.html"), 404


@app.errorhandler(OfferNotFound)
def restize_offer_not_found_error(error: OfferNotFound) -> ApiErrorResponse:
    error_details = {"offer": error.offer_id} if error.offer_id is not None else {}
    return app.generate_error_response(error_details), 404


@app.errorhandler(ApiErrors)
def restize_api_errors(error: ApiErrors) -> ApiErrorResponse:
    return app.generate_error_response(error.errors), error.status_code or 400


@app.errorhandler(core_exception.CoreException)
def restize_core_exception(error: core_exception.CoreException) -> ApiErrorResponse:
    mark_transaction_as_invalid()
    return app.generate_error_response(error.errors), 400


@app.errorhandler(Exception)
def internal_error(error: Exception) -> ApiErrorResponse | HTTPException:
    # pass through HTTP errors
    if isinstance(error, HTTPException):
        return error
    mark_transaction_as_invalid()
    logger.exception("Unexpected error on method=%s url=%s: %s", request.method, request.url, error)
    errors = ApiErrors()
    errors.add_error("global", "Il semble que nous ayons des problèmes techniques :( On répare ça au plus vite.")
    return app.generate_error_response(errors.errors), 500


@app.errorhandler(UnauthorizedError)
def unauthorized_error(error: UnauthorizedError) -> Response:
    headers: dict = {}
    if error.www_authenticate:
        headers["WWW-Authenticate"] = error.www_authenticate
        if error.realm:
            headers["WWW-Authenticate"] = '%s realm="%s"' % (headers["WWW-Authenticate"], error.realm)
    return Response(json.dumps(error.errors), 401, headers, mimetype="application/json")


@app.errorhandler(MethodNotAllowed)
def method_not_allowed(error: MethodNotAllowed) -> ApiErrorResponse:
    mark_transaction_as_invalid()
    api_errors = ApiErrors()
    api_errors.add_error("global", "La méthode que vous utilisez n'existe pas sur notre serveur")
    logger.warning("405 %s", error)
    return app.generate_error_response(api_errors.errors), 405


@app.errorhandler(DecimalCastError)
def decimal_cast_error(error: DecimalCastError) -> ApiErrorResponse:
    mark_transaction_as_invalid()
    api_errors = ApiErrors()
    logger.warning(json.dumps(error.errors))
    for field in error.errors.keys():
        api_errors.add_error(field, "Saisissez un nombre valide")
    return app.generate_error_response(api_errors.errors), 400


@app.errorhandler(DateTimeCastError)
def date_time_cast_error(error: DateTimeCastError) -> ApiErrorResponse:
    mark_transaction_as_invalid()
    api_errors = ApiErrors()
    logger.warning(json.dumps(error.errors))
    for field in error.errors.keys():
        api_errors.add_error(field, "Format de date invalide")
    return app.generate_error_response(api_errors.errors), 400


@app.errorhandler(finance_exceptions.DepositTypeAlreadyGrantedException)
def already_activated_exception(error: finance_exceptions.DepositTypeAlreadyGrantedException) -> ApiErrorResponse:
    mark_transaction_as_invalid()
    logger.error(json.dumps(error.errors))
    return app.generate_error_response(error.errors), 405


@app.errorhandler(429)
def ratelimit_handler(error: Exception) -> ApiErrorResponse:
    mark_transaction_as_invalid()
    identifier = None
    try:
        if request.is_json and "identifier" in request.json:
            identifier = request.json["identifier"]
    except (json.JSONDecodeError, werkzeug_exceptions.BadRequest) as e:
        logger.info("Could not extract user identifier from request: %s", e)
    try:
        auth = request.authorization
    except UnicodeDecodeError:
        # `werkzeug.http.parse_authorization_header()` raises a
        # UnicodeDecodeError if the login or the password contains
        # characters that have not been encoded in "utf-8", which
        # we would happily send to Sentry, where the password could
        # appear as clear text.
        pass
    else:
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
    return app.generate_error_response(api_errors.errors), 429


@app.errorhandler(DatabaseError)
def database_error_handler(error: DatabaseError) -> ApiErrorResponse:
    mark_transaction_as_invalid()
    if error.statement:
        try:
            sql_info_extra = {"sql_query": error.statement % format_sql_statement_params(error.params)}  # type: ignore [arg-type]
        except Exception:
            # `format_sql_statement_params()` cannot handle `params`
            # when it's a list, which happens when `executemany()` is
            # used.
            sql_info_extra = {"sql_query": error.statement, "sql_params": str(error.params)}
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
    return app.generate_error_response(errors.errors), 500


@app.errorhandler(ImageRatioError)
def handle_ratio_error(error: ImageRatioError) -> ApiErrorResponse:
    mark_transaction_as_invalid()
    logger.info("Image ratio error: %s", error)
    return app.generate_error_response({"code": "BAD_IMAGE_RATIO", "extra": str(error)}), 400


@app.errorhandler(sirene_exceptions.UnknownEntityException)
def handle_unknown_entity_exception(error: sirene_exceptions.UnknownEntityException) -> ApiErrorResponse:
    mark_transaction_as_invalid()
    msg = "Le SIREN n’existe pas."
    err = {"global": [msg]}
    return app.generate_error_response(err), 400


@app.errorhandler(sirene_exceptions.InvalidFormatException)
def handle_sirene_invalid_format_exception(error: sirene_exceptions.InvalidFormatException) -> ApiErrorResponse:
    mark_transaction_as_invalid()
    msg = "Le format de ce SIREN ou SIRET est incorrect."
    err = {"global": [msg]}
    return app.generate_error_response(err), 400


@app.errorhandler(sirene_exceptions.NonPublicDataException)
def handle_sirene_non_public_data_exception(error: sirene_exceptions.NonPublicDataException) -> ApiErrorResponse:
    mark_transaction_as_invalid()
    msg = "Les informations relatives à ce SIREN ou SIRET ne sont pas accessibles."
    err = {"global": [msg]}
    return app.generate_error_response(err), 400


@app.errorhandler(sirene_exceptions.ApiException)
def handle_sirene_api_exception(error: sirene_exceptions.ApiException) -> ApiErrorResponse:
    mark_transaction_as_invalid()
    msg = "Les informations relatives à ce SIREN ou SIRET n'ont pas pu être vérifiées, veuillez réessayer plus tard."
    err = {"global": [msg]}
    return app.generate_error_response(err), 500
