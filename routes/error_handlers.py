""" error handlers """
import traceback

import simplejson as json
from flask import current_app as app, jsonify, request
from werkzeug.exceptions import NotFound

from domain.stocks import TooLateToDeleteError
from domain.user_activation import AlreadyActivatedException
from models.api_errors import ApiErrors, ResourceGoneError, ResourceNotFoundError, ForbiddenError, DecimalCastError, \
    DateTimeCastError
from routes.before_request import InvalidOriginHeader
from utils.human_ids import NonDehumanizableId


@app.errorhandler(NotFound)
def restize_not_found_route_errors(e):
    return {}, 404


@app.errorhandler(ApiErrors)
def restize_api_errors(e):
    app.logger.error(json.dumps(e.errors))
    return jsonify(e.errors), e.status_code or 400


@app.errorhandler(TooLateToDeleteError)
def restize_too_late_to_delete_error(e):
    app.logger.error(json.dumps(e.errors))
    return jsonify(e.errors), e.status_code or 400


@app.errorhandler(ForbiddenError)
def restize_forbidden_error(e):
    app.logger.error(json.dumps(e.errors))
    return jsonify(e.errors), 403


@app.errorhandler(ResourceGoneError)
def restize_resource_gone_error(e):
    app.logger.error(json.dumps(e.errors))
    return jsonify(e.errors), e.status_code or 410


@app.errorhandler(ResourceNotFoundError)
def restize_booking_not_found_error(e):
    app.logger.error(json.dumps(e.errors))
    return jsonify(e.errors), e.status_code or 404


@app.errorhandler(InvalidOriginHeader)
def restize_invalid_header_exception(e):
    e = ApiErrors()
    e.add_error('global',
               'Header non autorisé')
    return jsonify(e.errors), 400


@app.errorhandler(500)
@app.errorhandler(Exception)
def internal_error(error):
    tb = traceback.format_exc()
    oneline_stack = ''.join(tb).replace('\n', ' ### ')
    app.logger.error('500 on %s %s — %s',
                     request.method, request.url, oneline_stack)
    e = ApiErrors()
    e.add_error('global',
               "Il semble que nous ayons des problèmes techniques :("
                + " On répare ça au plus vite.")
    return jsonify(e.errors), 500


@app.errorhandler(NonDehumanizableId)
def invalid_id_for_dehumanize_error(error):
    api_errors = ApiErrors()
    api_errors.add_error('global', 'La page que vous recherchez n\'existe pas')
    app.logger.error('404 %s' % str(error))
    return jsonify(api_errors.errors), 404


@app.errorhandler(DecimalCastError)
def decimal_cast_error(error):
    api_errors = ApiErrors()
    app.logger.warning(json.dumps(error.errors))
    for field in error.errors.keys():
        api_errors.add_error(field, 'Saisissez un nombre valide')
    return jsonify(api_errors.errors), 400


@app.errorhandler(DateTimeCastError)
def date_time_cast_error(error):
    api_errors = ApiErrors()
    app.logger.warning(json.dumps(error.errors))
    for field in error.errors.keys():
        api_errors.add_error(field, 'Format de date invalide')
    return jsonify(api_errors.errors), 400


@app.errorhandler(AlreadyActivatedException)
def already_activated_exception(error):
    app.logger.error(json.dumps(error.errors))
    return jsonify(error.errors), 405
