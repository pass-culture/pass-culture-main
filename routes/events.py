"""events"""
from flask import current_app as app, jsonify, request
from flask_login import current_user

from utils.includes import EVENT_INCLUDES
from utils.rest import expect_json_data,\
                       load_or_404,\
                       login_or_api_key_required,\
                       update

Event = app.model.Event
EventType = app.model.EventType



@app.route('/eventTypes', methods=['GET'])
def list_event_types():
    event_types = [{'label': et.value, 'value': str(et)}
                   for et in app.model.EventType]
    return jsonify(event_types), 200


@app.route('/events/<id>', methods=['GET'])
@login_or_api_key_required
def get_event(id):
    event = load_or_404(Event, id)
    return jsonify(
        event._asdict(
            include=EVENT_INCLUDES,
            has_dehumanized_id=True,
            has_model_name=True
        )
    ), 200


@app.route('/events', methods=['POST'])
@login_or_api_key_required
@expect_json_data
def post_event():
    event = Event()
    update(event, request.json)
    app.model.PcObject.check_and_save(event)
    return jsonify(
        event._asdict(
            include=EVENT_INCLUDES,
            has_dehumanized_id=True,
            has_model_name=True
        )
    ), 201


@app.route('/events/<id>', methods=['PATCH'])
@login_or_api_key_required
@expect_json_data
def patch_event(id):
    event = load_or_404(Event, id)
    update(event, request.json)
    app.model.PcObject.check_and_save(event)
    return jsonify(
        event._asdict(
            include=EVENT_INCLUDES,
            has_dehumanized_id=True,
            has_model_name=True
        )
    ), 200
