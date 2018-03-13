from base64 import b64decode
from flask import abort, current_app as app, jsonify, request

from utils.human_ids import dehumanize, humanize
from utils.object_storage import store_public_object
from utils.rest import expect_json_data,\
                       handle_rest_get_list,\
                       update

venueModel = app.model.Venue


def store_public_venue_objects(venueId, json):
    humanized_venue_id = humanize(venueId)
    if 'spreadsheet_content' in json:
        store_public_object('spreadsheets',
            'venues/' + humanized_venue_id,
            b64decode(json['spreadsheet_content']),
            'application/CSV'
        )
    if 'thumb_content' in json:
        store_public_object('thumbs',
            'venues/' + humanized_venue_id,
            b64decode(json['thumb_content']),
            json['thumb_content_type']
        )
    if 'zip_content' in json:
        store_public_object('zips',
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
    new_venue = venueModel(from_dict=request.json)
    app.model.PcObject.check_and_save(new_venue)

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
