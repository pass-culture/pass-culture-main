"""providers"""
from flask import current_app as app, jsonify

AUTHORIZED_LOCAL_PROVIDERS = [
    app.local_providers.OpenAgendaEvents
]


@app.route('/providerTypes', methods=['GET'])
def list_providers():
    """
    print('app.local_providers.values()', app.local_providers.values())
    offerProviders = filter(
        lambda p: p.objectType == app.model.Offer\
        and p != app.local_providers.SpreadsheetOffers,
        app.local_providers.values()
    )
    """
    providers = AUTHORIZED_LOCAL_PROVIDERS
    return jsonify(
        [
            {'localClass': p.__name__, 'name': p.name}
            for p in providers
        ]
    )
