"""types"""
from flask import current_app as app, jsonify

EventType = app.model.EventType
ThingType = app.model.ThingType

@app.route('/types', methods=['GET'])
def list_types():
    event_types = [{'label': et.value, 'value': str(et)}
                   for et in app.model.EventType]
    thing_types = [{'label': et.value, 'value': str(et)}
                   for et in app.model.ThingType]
    return jsonify(event_types + thing_types), 200
