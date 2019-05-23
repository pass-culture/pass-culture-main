"""providers"""
from flask import current_app as app, jsonify

import local_providers
from models.provider import Provider


@app.route('/providers', methods=['GET'])
def list_providers():
    providers = Provider\
                         .query.filter_by(isActive=True)\
                         .all()
    result = []
    for p in providers:
        p_dict = p.as_dict()
        if p.localClass is not None and hasattr(local_providers, p.localClass):
            providerClass = getattr(local_providers, p.localClass)
            p_dict['identifierRegexp'] = providerClass.identifierRegexp
            p_dict['identifierDescription'] = providerClass.identifierDescription
        del p_dict['apiKey']
        del p_dict['apiKeyGenerationDate']
        result.append(p_dict)
    return jsonify(result)
