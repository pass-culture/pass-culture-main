from flask import current_app as app, jsonify

from repository import feature_queries

@app.route('/features', methods=['GET'])
def list_features():
    features = feature_queries.find_all()
    return jsonify([_clean_feature_dict(feature) for feature in features])


def _clean_feature_dict(feature):
    return dict(
        feature.as_dict(),
        **{ "name": str(feature.name).replace('FeatureToggle.', '') }
    )
