from flask import current_app as app, jsonify
from flask_login import login_required

from repository import feature_queries
from utils.includes import FEATURE_INCLUDES


@app.route('/features', methods=['GET'])
@login_required
def list_features():
    features = feature_queries.find_all()
    serialized_features = [f.as_dict(include=FEATURE_INCLUDES) for f in features]
    return jsonify(serialized_features), 200