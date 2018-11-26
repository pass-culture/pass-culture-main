""" venues """
from flask import current_app as app, jsonify, request
from flask_login import login_required

from domain.admin_emails import send_venue_validation_email
from models import ApiErrors
from models.user_offerer import RightsType
from models.venue import Venue
from repository.venue_queries import save_venue, find_venues
from utils.includes import VENUE_INCLUDES
from utils.mailing import MailServiceException
from utils.rest import ensure_current_user_has_rights, \
                       expect_json_data, \
                       load_or_404
from validation.venues import validate_coordinates, check_valid_edition, check_get_venues_params
from validation.exports import check_user_is_admin


@app.route('/venues/<venueId>', methods=['GET'])
@login_required
def get_venue(venueId):
    venue = load_or_404(Venue, venueId)
    ensure_current_user_has_rights(RightsType.editor, venue.managingOffererId)
    return jsonify(venue._asdict(include=VENUE_INCLUDES))


@app.route('/venues', methods=['POST'])
@login_required
@expect_json_data
def create_venue():
    validate_coordinates(request.json.get('latitude', None), request.json.get('longitude', None))
    venue = Venue(from_dict=request.json)
    venue.departementCode = 'XX'  # avoid triggerring check on this
    siret = request.json.get('siret')
    if not siret:
        venue.generate_validation_token()
    save_venue(venue)

    if not venue.isValidated:
        try:
            send_venue_validation_email(venue, app.mailjet_client.send.create)
        except MailServiceException as e:
            app.logger.error('Mail service failure', e)

    return jsonify(venue._asdict(include=VENUE_INCLUDES)), 201


@app.route('/venues/<venueId>', methods=['PATCH'])
@login_required
@expect_json_data
def edit_venue(venueId):
    check_valid_edition(request)
    venue = load_or_404(Venue, venueId)
    validate_coordinates(request.json.get('latitude', None), request.json.get('longitude', None))
    ensure_current_user_has_rights(RightsType.editor, venue.managingOffererId)
    venue.populateFromDict(request.json)
    save_venue(venue)
    return jsonify(venue._asdict(include=VENUE_INCLUDES)), 200


@app.route('/venues', methods=['GET'])
@login_required
def get_venues():
    check_user_is_admin(current_user)

    params_keys = ['dpt', 'has_validated_offerer', 'zip_codes', 'from_date', 'to_date', 'has_siret', 'venue_type', 'has_offer']
    params = {}
    for key in params_keys:
        if key == 'dpt' or key == 'zip_codes':
            params[key] = request.args.getlist(key)    
        else:
            params[key] = request.args.get(key)

    check_get_venues_params(params)
    result = find_venues(dpt=params['dpt'], zip_codes=params['zip_codes'], from_date=params['from_date'], to_date=params['to_date'],
     has_siret=params['has_siret'], venue_type=params['venue_type'], has_offer=params['has_offer'])

    return jsonify(result), 200
