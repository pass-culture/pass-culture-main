"""providers"""
from flask import current_app as app, jsonify

PROVIDER_LOCAL_CLASSES = [
    'OpenAgendaEvents'
]

@app.route('/providers', methods=['GET'])
def list_providers():
    providers = app.model.Provider\
                         .query\
                         .filter(
                             app.model.Provider.localClass.in_(PROVIDER_LOCAL_CLASSES)
                         ).all()
    return jsonify([p._asdict() for p in providers])
