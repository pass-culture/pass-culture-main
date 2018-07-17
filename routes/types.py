"""types"""
from flask import current_app as app, jsonify

EventType = EventType
ThingType = ThingType

@app.route('/types', methods=['GET'])
def list_types():
    event_types = [{'label': et.value, 'value': str(et), 'type': 'Event'}
                   for et in EventType]
    thing_types = [{'label': et.value, 'value': str(et), 'type': 'Thing'}
                   for et in ThingType]
    return jsonify([{'id': i, **x} for i, x in enumerate(event_types + thing_types)]), 200
