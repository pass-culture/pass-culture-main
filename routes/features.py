import json

from flask import current_app as app

from repository import feature_queries


@app.route('/features', methods=['GET'])
def list_features():
    features = feature_queries.find_all()
    features_dict = {
        _clean_feature_name(f): f.isActive
        for f in features
    }
    features_js = 'var features = ' + json.dumps(features_dict)
    return features_js, 200, {'Content-type': 'text/javascript; charset=utf-8;'}


def _clean_feature_name(f):
    return str(f.name).replace('FeatureToggle.', '')
