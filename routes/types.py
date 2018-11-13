"""types"""
from flask import current_app as app, jsonify
from flask_login import current_user

from domain.types import get_formatted_event_or_thing_types


@app.route('/types', methods=['GET'])
def list_types():
    return jsonify(get_formatted_event_or_thing_types(as_admin=current_user.isAdmin)), 200
