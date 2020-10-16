from flask import jsonify
from flask_login import login_required

from pcapi.flask_app import private_api
from pcapi.domain.music_types import music_types


@private_api.route('/musicTypes', methods=['GET'])
@login_required
def list_music_types():
    return jsonify(music_types), 200
