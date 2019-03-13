from flask import current_app as app, jsonify
from flask_login import login_required

from repository import feature_queries
from utils.includes import FEATURE_INCLUDES


@app.route('/features', methods=['GET'])
@login_required
def list_features():
    features = feature_queries.find_all()
    dictified_features = [f._asdict(include=FEATURE_INCLUDES) for f in features]
    return jsonify(dictified_features), 200