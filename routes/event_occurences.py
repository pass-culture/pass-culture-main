""" venues """
from flask import current_app as app, jsonify, request

from utils.config import DELETE
from utils.human_ids import dehumanize
from utils.includes import VENUES_INCLUDES
from utils.rest import current_user,\
                       delete,\
                       ensure_current_user_has_rights,\
                       expect_json_data,\
                       load_or_404,\
                       handle_rest_get_list,\
                       update


EventOccurence = app.model.EventOccurence


@app.route('/eventOccurences', methods=['GET'])
def list_event_occurences():
    return handle_rest_get_list(app.model.EventOccurence)


@app.route('/eventOccurences/<id>', methods=['GET'])
def get_event_occurence(venueId):
    eo = load_or_404(EventOccurence, id)
    return jsonify(eo._asdict())


@app.route('/eventOccurences', methods=['POST'])
@expect_json_data
def create_event_occurence():
    eo = EventOccurence(from_dict=request.json)
    ensure_current_user_has_rights(app.model.RightsType.editor,
                                   eo.venue.managingOffererId)
    app.model.PcObject.check_and_save(eo)
    return jsonify(eo._asdict()), 201


@app.route('/eventOccurences/<id>', methods=['PATCH'])
@expect_json_data
def edit_event_occurence(id):
    eo = load_or_404(EventOccurence, id)
    ensure_current_user_has_rights(app.model.RightsType.editor,
                                   eo.venue.managingOffererId)
    update(eo, request.json)
    #TODO: Si changement d'horaires et qu'il y a des réservations il faut envoyer des mails !
    #TODO: Interdire la modification d'évenements passés
    app.model.PcObject.check_and_save(eo)
    return jsonify(eo._asdict(include=VENUES_INCLUDES)), 200


@app.route('/eventOccurences/<id>', methods=['DELETE'])
@expect_json_data
def delete_event_occurence(id):
    eo = load_or_404(EventOccurence, id)
    ensure_current_user_has_rights(app.model.RightsType.editor,
                                   eo.venue.managingOffererId)
    #TODO: S'il y a des réservations il faut envoyer des mails !
    #TODO: Interdire la suppression d'évenements passés
    return delete(eo, request.json)
