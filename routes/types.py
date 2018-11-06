"""types"""
from flask import current_app as app, jsonify

from domain.types import get_formatted_types


@app.route('/types', methods=['GET'])
def list_types():
    return jsonify(get_formatted_types()), 200
