"""providers"""
from flask import current_app as app, jsonify

from repository.provider_queries import get_enabled_providers_for_pro
from routes.serialization import as_dict


@app.route('/providers', methods=['GET'])
def list_providers():
    providers = get_enabled_providers_for_pro()
    result = []
    for provider in providers:
        p_dict = as_dict(provider)
        del p_dict['apiKey']
        del p_dict['apiKeyGenerationDate']
        result.append(p_dict)
    return jsonify(result)
