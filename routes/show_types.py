from flask import current_app as app, jsonify
from flask_login import current_user, login_required

from domain.show_types import show_types


@app.route('/showTypes', methods=['GET'])
@login_required
def list_show_types():
    return jsonify(show_types), 200
