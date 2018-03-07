from flask import current_app as app, jsonify


@app.route('/providers', methods=['GET'])
def list_providers():
    offerProviders = filter(
        lambda p: p.objectType == app.model.Offer\
        and p != app.local_providers.SpreadsheetOffers,
        app.local_providers.values()
    )
    return jsonify(list(map(
        lambda p: {'localClass': p.__name__, 'name': p.name},
    offerProviders)))
