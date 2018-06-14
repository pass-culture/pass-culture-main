""" venues """
from flask import current_app as app, jsonify, request

from utils.config import DELETE
from utils.human_ids import dehumanize
from utils.includes import VENUES_INCLUDES
from utils.rest import current_user,\
                       ensure_current_user_has_rights,\
                       expect_json_data,\
                       load_or_404,\
                       handle_rest_get_list,\
                       update


Venue = app.model.Venue


@app.route('/venues', methods=['GET'])
def list_venues():
    return handle_rest_get_list(app.model.Venue)


@app.route('/venues/<venueId>', methods=['GET'])
def get_venue(venueId):
    venue = load_or_404(Venue, venueId)
    return jsonify(venue._asdict(include=VENUES_INCLUDES))


@app.route('/venues', methods=['POST'])
@expect_json_data
def create_venue():
    venue = Venue(from_dict=request.json)
    venue.departementCode = 'XX'  # avoid triggerring check on this
    app.model.PcObject.check_and_save(venue)
    return jsonify(venue._asdict(include=VENUES_INCLUDES)), 201


@app.route('/venues/<venueId>', methods=['PATCH'])
@expect_json_data
def edit_venue(venueId):
    venue = load_or_404(Venue, venueId)
    ensure_current_user_has_rights(app.model.RightsType.editor,
                                   venue.managingOffererId)
    update(venue, request.json)
    app.model.PcObject.check_and_save(venue)
    return jsonify(venue._asdict(include=VENUES_INCLUDES)), 200
