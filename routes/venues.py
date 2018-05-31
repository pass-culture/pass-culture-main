""" venues """
from base64 import b64decode
from flask import current_app as app, jsonify, request
from flask_login import current_user

from utils.human_ids import dehumanize, humanize
from utils.object_storage import store_public_object
from utils.rest import expect_json_data,\
                       handle_rest_get_list,\
                       update

venueModel = app.model.Venue
offererModel = app.model.Offerer
userOffererModel = app.model.UserOfferer

VENUE_KEYS = [
    'siret',
    'name',
    'address',
    'latitude',
    'longitude'
]

def feed_venue(venue, json):
    for venue_key in VENUE_KEYS:
        if venue_key in json:
            venue.__setattr__(venue_key, json[venue_key])

OFFERER_KEYS = [
    'bookingEmail'
]

def feed_offerer(offerer, json):
    for offerer_key in OFFERER_KEYS:
        if offerer_key in json:
            offerer.__setattr__(offerer_key, json[offerer_key])

def store_public_venue_objects(venueId, json):
    humanized_venue_id = humanize(venueId)
    if 'spreadsheet_content' in json:
        store_public_object(
            'spreadsheets',
            'venues/' + humanized_venue_id,
            b64decode(json['spreadsheet_content']),
            'application/CSV'
        )
    if 'thumb_content' in json:
        store_public_object(
            'thumbs',
            'venues/' + humanized_venue_id,
            b64decode(json['thumb_content']),
            json['thumb_content_type']
        )
    if 'zip_content' in json:
        store_public_object(
            'zips',
            'venues/' + humanized_venue_id,
            b64decode(json['zip_content']),
            'application/zip'
        )


@app.route('/venues', methods=['GET'])
def list_venues():
    return handle_rest_get_list(venueModel)


@app.route('/venues/<venueId>', methods=['GET'])
def get_venue(venueId):
    query = venueModel.query.filter_by(id=dehumanize(venueId))
    venue = query.first_or_404()
    return jsonify(venue._asdict())


@app.route('/venues', methods=['POST'])
@expect_json_data
def create_venue():
    new_venue = venueModel()
    feed_venue(new_venue, request.json)
    app.model.PcObject.check_and_save(new_venue)
    new_offerer = offererModel()
    new_offerer.venue = new_venue
    new_offerer.name = new_venue.name
    new_offerer.address = new_venue.address
    feed_offerer(new_offerer, request.json )

    app.model.PcObject.check_and_save(new_offerer)

    user_offerer = userOffererModel()
    user_offerer.offerer = new_offerer
    user_offerer.user = current_user

    app.model.PcObject.check_and_save(user_offerer)

    if 'thumb_content' in request.json:
        store_public_venue_objects(new_venue.id, request.json)
    return jsonify(new_venue._asdict()), 201


@app.route('/venues/<venueId>', methods=['PATCH'])
@expect_json_data
def edit_venue(venueId):
    updated_venue_dict = request.json
    venueId = venueId
    query = venueModel.query.filter_by(id=dehumanize(venueId))
    venue = query.first_or_404()
    update(venue, updated_venue_dict)
    app.model.PcObject.check_and_save(venue)
    store_public_venue_objects(venue.id, request.json)
    return jsonify(venue._asdict()), 200
