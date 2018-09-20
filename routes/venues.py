""" venues """
from flask import current_app as app, jsonify, request
from flask_login import login_required

from models.user_offerer import RightsType
from models.venue import Venue
from repository.venue_queries import save_venue
from utils.includes import VENUE_INCLUDES
from utils.rest import ensure_current_user_has_rights, \
    expect_json_data, \
    load_or_404, \
    handle_rest_get_list
from validation.venues import validate_coordinates


@app.route('/venues', methods=['GET'])
@login_required
def list_venues():
    return handle_rest_get_list(Venue, order_by=Venue.name)


@app.route('/venues/<venueId>', methods=['GET'])
@login_required
def get_venue(venueId):
    venue = load_or_404(Venue, venueId)
    return jsonify(venue._asdict(include=VENUE_INCLUDES))


@app.route('/venues', methods=['POST'])
@login_required
@expect_json_data
def create_venue():
    validate_coordinates(request.json.get('latitude', None), request.json.get('longitude', None))
    venue = Venue(from_dict=request.json)
    venue.departementCode = 'XX'  # avoid triggerring check on this
    save_venue(venue)
    return jsonify(venue._asdict(include=VENUE_INCLUDES)), 201


@app.route('/venues/<venueId>', methods=['PATCH'])
@login_required
@expect_json_data
def edit_venue(venueId):
    venue = load_or_404(Venue, venueId)
    validate_coordinates(request.json.get('latitude', None), request.json.get('longitude', None))
    ensure_current_user_has_rights(RightsType.editor, venue.managingOffererId)
    venue.populateFromDict(request.json)
    save_venue(venue)
    return jsonify(venue._asdict(include=VENUE_INCLUDES)), 200
