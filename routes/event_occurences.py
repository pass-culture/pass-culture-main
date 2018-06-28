""" event_occurences """
from flask import current_app as app, jsonify, request

from utils.includes import EVENT_OCCURENCE_INCLUDES
from utils.rest import delete,\
                       ensure_current_user_has_rights,\
                       ensure_can_be_updated,\
                       expect_json_data,\
                       load_or_404,\
                       login_or_api_key_required,\
                       handle_rest_get_list,\
                       update

Event = app.model.Event
EventOccurence = app.model.EventOccurence
Offer = app.model.Offer
Venue = app.model.Venue

@app.route('/eventOccurences', methods=['GET'])
@login_or_api_key_required
def list_event_occurences():
    return handle_rest_get_list(app.model.EventOccurence)


@app.route('/eventOccurences/<id>', methods=['GET'])
@login_or_api_key_required
def get_event_occurence(id):
    eo = load_or_404(EventOccurence, id)
    return jsonify(eo._asdict(include=EVENT_OCCURENCE_INCLUDES))


@app.route('/eventOccurences', methods=['POST'])
@login_or_api_key_required
@expect_json_data
def create_event_occurence():
    ensure_can_be_updated(Event, request.json['eventId'])

    eo = EventOccurence(from_dict=request.json)
    venue = load_or_404(Venue, request.json['venueId'])
    ensure_current_user_has_rights(app.model.RightsType.editor,
                                   venue.managingOffererId)

    app.model.PcObject.check_and_save(eo)
    return jsonify(eo._asdict(include=EVENT_OCCURENCE_INCLUDES)), 201


@app.route('/eventOccurences/<id>', methods=['PATCH'])
@login_or_api_key_required
@expect_json_data
def edit_event_occurence(id):

    eo = ensure_can_be_updated(EventOccurence, id)

    ensure_current_user_has_rights(app.model.RightsType.editor,
                                   eo.venue.managingOffererId)
    update(eo, request.json)
    #TODO: Si changement d'horaires et qu'il y a des réservations il faut envoyer des mails !
    #TODO: Interdire la modification d'évenements passés
    app.model.PcObject.check_and_save(eo)

    return jsonify(eo._asdict(include=EVENT_OCCURENCE_INCLUDES)), 200


@app.route('/eventOccurences/<id>', methods=['DELETE'])
@login_or_api_key_required
@expect_json_data
def delete_event_occurence(id):
    eo = load_or_404(EventOccurence, id)
    ensure_current_user_has_rights(app.model.RightsType.editor,
                                   eo.venue.managingOffererId)
    #TODO: S'il y a des réservations il faut envoyer des mails !
    #TODO: Interdire la suppression d'évenements passés
    return delete(eo, request.json)
