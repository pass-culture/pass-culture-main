""" error handlers """
import simplejson as json
from flask import current_app as app, jsonify

from models.api_errors import ApiErrors, ResourceGoneError
from repository.booking_queries import BookingNotFound


@app.errorhandler(ApiErrors)
def restize_api_errors(e):
    print(json.dumps(e.errors))
    return jsonify(e.errors), e.status_code or 400


@app.errorhandler(ResourceGoneError)
def restize_resource_gone_error(e):
    app.logger.error(json.dumps(e.errors))
    return jsonify(e.errors), e.status_code or 410


@app.errorhandler(BookingNotFound)
def restize_booking_not_found_error(e):
    return jsonify(e.errors), e.status_code or 404
