"""providers"""
from flask import current_app as app, jsonify

@app.route('/providers', methods=['GET'])
def list_providers():
    providers = app.model.Provider\
                         .queryActive\
                         .all()
    return jsonify([p._asdict() for p in providers])
