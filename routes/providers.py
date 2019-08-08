"""providers"""
from flask import current_app as app, jsonify

import local_providers
from repository.provider_queries import get_enabled_providers_for_pro
from routes.serializer import as_dict


@app.route('/providers', methods=['GET'])
def list_providers():
    providers = get_enabled_providers_for_pro()
    result = []
    for provider in providers:
        p_dict = as_dict(provider)
        if provider.localClass is not None and hasattr(local_providers, provider.localClass):
            provider_class = getattr(local_providers, provider.localClass)
            p_dict['identifierRegexp'] = provider_class.identifierRegexp
            p_dict['identifierDescription'] = provider_class.identifierDescription
        del p_dict['apiKey']
        del p_dict['apiKeyGenerationDate']
        result.append(p_dict)
    return jsonify(result)

