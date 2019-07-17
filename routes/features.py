from flask import current_app as app, jsonify

from models.feature import Feature
from repository import feature_queries

@app.route('/features', methods=['GET'])
def list_features():
    features = feature_queries.find_all()
    return jsonify([feature.as_dict() for feature in features])
