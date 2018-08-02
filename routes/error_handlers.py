""" error handlers """
import simplejson as json
from flask import current_app as app, jsonify

from models.api_errors import ApiErrors

@app.errorhandler(ApiErrors)
def restize_api_errors(e):
    print(json.dumps(e.errors))
    return jsonify(e.errors), e.status_code or 400
