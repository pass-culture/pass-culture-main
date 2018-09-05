"""types"""
from flask import current_app as app, jsonify

from models.event import EventType
from models.thing import ThingType


def format_type(t, model_name):
    result = t.value
    result['value'] = str(t)
    result['type'] = model_name
    return result


@app.route('/types', methods=['GET'])
def list_types():
    event_types = [format_type(et, 'Event') for et in EventType]
    thing_types = [format_type(et, 'Thing') for et in ThingType]
    return jsonify(event_types + thing_types), 200
