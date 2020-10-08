from flask import current_app as app, jsonify

from pcapi.repository import feature_queries
from pcapi.routes.serialization import as_dict
from pcapi.utils.includes import FEATURE_INCLUDES


@app.route('/features', methods=['GET'])
def list_features():
    features = feature_queries.find_all()
    return jsonify([as_dict(feature, includes=FEATURE_INCLUDES) for feature in features]), 200
