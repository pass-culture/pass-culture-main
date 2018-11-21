""" error handlers """
import traceback

import simplejson as json
from flask import current_app as app, jsonify, request

from models.api_errors import ApiErrors, ResourceGoneError, ResourceNotFound, ForbiddenError, DecimalCastError
from routes.before_request import InvalidOriginHeader
from utils.human_ids import NonDehumanizableId


@app.errorhandler(ApiErrors)
def restize_api_errors(e):
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


@app.errorhandler(ResourceNotFound)
def restize_booking_not_found_error(e):
    app.logger.error(json.dumps(e.errors))
    return jsonify(e.errors), e.status_code or 404


@app.errorhandler(InvalidOriginHeader)
def restize_invalid_header_exception(e):
    e = ApiErrors()
    e.addError('global',
               'Header non autorisé')
    return jsonify(e.errors), 400


@app.errorhandler(500)
def internal_error(error):
    tb = traceback.format_exc()
    oneline_stack = ''.join(tb).replace('\n', ' ### ')
    app.logger.error('500 on %s %s — %s',
                     request.method, request.url, oneline_stack)
    e = ApiErrors()
    e.addError('global',
               "Il semble que nous ayons des problèmes techniques :("
               + " On répare ça au plus vite.")
    return jsonify(e.errors), 500


@app.errorhandler(NonDehumanizableId)
def invalid_id_for_dehumanize_error(error):
    api_errors = ApiErrors()
    api_errors.addError('global', 'La page que vous recherchez n\'existe pas')
    app.logger.error('404 %s' % str(error))
    return jsonify(api_errors.errors), 404


@app.errorhandler(DecimalCastError)
def invalid_data_format(error):
    api_errors = ApiErrors()
    for field in error.errors.keys():
        api_errors.addError(field, 'Caractère interdit')
    return jsonify(api_errors.errors), 400
