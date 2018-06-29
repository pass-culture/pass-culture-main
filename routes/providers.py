"""providers"""
from flask import current_app as app, jsonify

@app.route('/providers', methods=['GET'])
def list_providers():
    providers = app.model.Provider\
                         .query.filter_by(isActive=True)\
                         .all()
    result = []
    for p in providers:
        p_dict = p._asdict()
        if p.localClass is not None and p.localClass in app.local_providers:
            providerClass = app.local_providers[p.localClass]
            p_dict['identifierRegexp'] = providerClass.identifierRegexp
            p_dict['identifierDescription'] = providerClass.identifierDescription
        del p_dict['apiKey']
        del p_dict['apiKeyGenerationDate']
        result.append(p_dict)
    return jsonify(result)
