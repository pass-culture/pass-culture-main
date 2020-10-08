from flask import current_app as app, jsonify
from flask_login import login_required

from pcapi.domain.music_types import music_types


@app.route('/musicTypes', methods=['GET'])
@login_required
def list_music_types():
    return jsonify(music_types), 200
