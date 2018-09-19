"""types"""
from flask import current_app as app, jsonify

from domain.types import get_format_types

@app.route('/types', methods=['GET'])
def list_types():
    return jsonify(get_format_types()), 200
