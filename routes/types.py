"""types"""
from flask import current_app as app, jsonify
from flask_login import current_user, login_required

from domain.types import get_formatted_event_or_thing_types
from models.feature import FeatureToggle
from utils.feature import feature_required
from utils.rest import expect_json_data


@app.route('/types', methods=['GET'])
@login_required
def list_types():
    return jsonify(get_formatted_event_or_thing_types(with_activation_type=current_user.isAdmin)), 200
