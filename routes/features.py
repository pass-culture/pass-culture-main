from flask import current_app as app, jsonify

from repository import feature_queries
from routes.serializer import as_dict


@app.route('/features', methods=['GET'])
def list_features():
    features = feature_queries.find_all()
    return jsonify([as_dict(feature) for feature in features]), 200
