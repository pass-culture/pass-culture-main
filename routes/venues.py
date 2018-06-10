""" venues """
from flask import current_app as app, jsonify, request

from utils.config import DELETE
from utils.human_ids import dehumanize
from utils.includes import VENUES_INCLUDES
from utils.provider import create_venue_provider
from utils.rest import expect_json_data,\
                       handle_rest_get_list,\
                       update

def update_venue(venue):
    if 'venueProviders' in request.json:
        for venue_provider_dict in request.json['venueProviders']:
            if venue_provider_dict.get('DELETE') == DELETE:
                app.model.VenueProvider.query.filter_by(
                    venueId=venue.id,
                    providerId=dehumanize(venue_provider_dict['providerId'])
                ).delete()
            else:
                create_venue_provider(
                    venue,
                    venue_provider_dict
                )
    update(venue, request.json, **{'skipped_keys': ['venueProviders']})
    app.model.PcObject.check_and_save(venue)

@app.route('/venues', methods=['GET'])
def list_venues():
    return handle_rest_get_list(app.model.Venue)


@app.route('/venues/<venueId>', methods=['GET'])
def get_venue(venueId):
    query = app.model.Venue.query.filter_by(id=dehumanize(venueId))
    venue = query.first_or_404()
    return jsonify(venue._asdict(include=VENUES_INCLUDES))


@app.route('/venues', methods=['POST'])
@expect_json_data
def create_venue():
    venue = app.model.Venue()
    update_venue(venue)
    return jsonify(venue._asdict(include=VENUES_INCLUDES)), 201


@app.route('/venues/<venueId>', methods=['PATCH'])
@expect_json_data
def edit_venue(venueId):
    venue = app.model.Venue\
                     .query.filter_by(id=dehumanize(venueId))\
                     .first_or_404()
    update_venue(venue)
    return jsonify(venue._asdict(include=VENUES_INCLUDES)), 200
