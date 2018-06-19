"""events"""
from flask import current_app as app, jsonify, request

from utils.includes import EVENT_INCLUDES
from utils.rest import expect_json_data,\
                       load_or_404,\
                       login_or_api_key_required,\
                       update

Event = app.model.Event


@app.route('/events/<id>', methods=['GET'])
@login_or_api_key_required
def get_event(id):
    event = load_or_404(Event, id)
    print('event.type', event.type)
    return jsonify(
        event._asdict(include=EVENT_INCLUDES)
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
