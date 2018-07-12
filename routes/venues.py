""" venues """
from flask import current_app as app, jsonify, request

from utils.config import DELETE
from utils.human_ids import dehumanize
from utils.includes import VENUE_INCLUDES
from utils.rest import current_user,\
                       ensure_current_user_has_rights,\
                       expect_json_data,\
                       load_or_404,\
                       handle_rest_get_list


RightsType = app.model.RightsType
Venue = app.model.Venue


@app.route('/venues', methods=['GET'])
def list_venues():
    return handle_rest_get_list(Venue)


@app.route('/venues/<venueId>', methods=['GET'])
def get_venue(venueId):
    venue = load_or_404(Venue, venueId)
    return jsonify(venue._asdict(include=VENUE_INCLUDES))


@app.route('/venues', methods=['POST'])
@expect_json_data
def create_venue():
    venue = Venue(from_dict=request.json)
    venue.departementCode = 'XX'  # avoid triggerring check on this
    app.model.PcObject.check_and_save(venue)
    return jsonify(venue._asdict(include=VENUE_INCLUDES)), 201


@app.route('/venues/<venueId>', methods=['PATCH'])
@expect_json_data
def edit_venue(venueId):
    venue = load_or_404(Venue, venueId)
    ensure_current_user_has_rights(RightsType.editor,
                                   venue.managingOffererId)
    venue.populateFromDict(request.json)
    app.model.PcObject.check_and_save(venue)
    return jsonify(venue._asdict(include=VENUE_INCLUDES)), 200
