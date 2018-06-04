""" venues """
from flask import current_app as app, jsonify, request

from utils.human_ids import dehumanize, humanize
from utils.object_storage import save_thumb
from utils.rest import expect_json_data,\
                       feed,\
                       handle_rest_get_list

VENUE_KEYS = [
    'siret',
    'name',
    'address',
    'latitude',
    'longitude',
    'managingOffererId'
]

@app.route('/venues', methods=['GET'])
def list_venues():
    return handle_rest_get_list(app.model.Venue)


@app.route('/venues/<venueId>', methods=['GET'])
def get_venue(venueId):
    query = app.model.Venue.query.filter_by(id=dehumanize(venueId))
    venue = query.first_or_404()
    return jsonify(venue._asdict())


@app.route('/venues', methods=['POST'])
@expect_json_data
def create_venue():
    new_venue = app.model.Venue()
    feed(new_venue, request.json, VENUE_KEYS)
    app.model.PcObject.check_and_save(new_venue)
    save_thumb(new_venue.id, request.json)
    return jsonify(new_venue._asdict()), 201


@app.route('/venues/<venueId>', methods=['PATCH'])
@expect_json_data
def edit_venue(venueId):
    venue = app.model.Venue\
                    .query.filter_by(id=dehumanize(venueId))\
                    .first_or_404()
    feed(venue, request.json, VENUE_KEYS)
    app.model.PcObject.check_and_save(venue)
    save_thumb(venue.id, request.json)
    return jsonify(venue._asdict()), 200
