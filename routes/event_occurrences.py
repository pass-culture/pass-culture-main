""" event_occurrences """
from flask import current_app as app, jsonify, request

from models import Event, EventOccurrence, Offer, PcObject, RightsType, Venue
from utils.human_ids import dehumanize
from utils.includes import EVENT_OCCURRENCE_INCLUDES
from utils.rest import delete, \
    ensure_current_user_has_rights, \
    expect_json_data, \
    load_or_404, \
    login_or_api_key_required, \
    handle_rest_get_list


@app.route('/eventOccurrences', methods=['GET'])
@login_or_api_key_required
def list_event_occurrences():
    return handle_rest_get_list(EventOccurrence)


@app.route('/eventOccurrences/<id>', methods=['GET'])
@login_or_api_key_required
def get_event_occurrence(id):
    eo = load_or_404(EventOccurrence, id)
    return jsonify(eo._asdict(include=EVENT_OCCURRENCE_INCLUDES))


@app.route('/eventOccurrences', methods=['POST'])
@login_or_api_key_required
@expect_json_data
def create_event_occurrence():
    event = Event.query.join(Offer)\
                       .filter(Offer.id == dehumanize(request.json['offerId']))\
                       .first_or_404()
    event.ensure_can_be_updated()

    eo = EventOccurrence(from_dict=request.json)
    venue = load_or_404(Venue, request.json['venueId'])
    ensure_current_user_has_rights(RightsType.editor,
                                   venue.managingOffererId)

    PcObject.check_and_save(eo)
    return jsonify(eo._asdict(include=EVENT_OCCURRENCE_INCLUDES)), 201


@app.route('/eventOccurrences/<id>', methods=['PATCH'])
@login_or_api_key_required
@expect_json_data
def edit_event_occurrence(id):
    eo = load_or_404(EventOccurrence, id)

    eo.ensure_can_be_updated()

    ensure_current_user_has_rights(RightsType.editor,
                                   eo.offer.venue.managingOffererId)
    eo.populateFromDict(request.json)
    #TODO: Si changement d'horaires et qu'il y a des réservations il faut envoyer des mails !
    #TODO: Interdire la modification d'évenements passés
    PcObject.check_and_save(eo)

    return jsonify(eo._asdict(include=EVENT_OCCURRENCE_INCLUDES)), 200


@app.route('/eventOccurrences/<id>', methods=['DELETE'])
@login_or_api_key_required
def delete_event_occurrence(id):
    eo = load_or_404(EventOccurrence, id)
    ensure_current_user_has_rights(RightsType.editor,
                                   eo.venue.managingOffererId)
    return delete(eo)
