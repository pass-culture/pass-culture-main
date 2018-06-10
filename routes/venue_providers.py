""" venues """
from os import path

from flask import current_app as app, jsonify, request

from utils.human_ids import dehumanize
from utils.rest import expect_json_data,\
                       update


VenueProvider = app.model.VenueProvider


@app.route('/venue_providers/<venueId>', methods=['POST'])
@expect_json_data
def create_venue_provider(venueId):
    new_vp = VenueProvider(from_dict=request.json)
    new_vp.venueId = venueId
    app.model.PcObject.check_and_save(new_vp)
    subprocess.Popen(['pc', 'update_providables', '-p', new_vp.provider.name,
                                                  '-v', new_vp.venueId],
                     cwd=Path(path.dirname(path.realpath(__file__))) / '..')
    return jsonify(new_vp._asdict()), 201


@app.route('/venue_providers/<venueId>/<providerId>', methods=['DELETE'])
@expect_json_data
def edit_venue_provider(venueId, providerId):
    vp = VenueProvider.query.filter_by(venueId=dehumanize(venueId),
                                       providerId=dehumanize(providerId))\
                      .first_or_404()
    update(vp, request.json)
    #TODO: remove things from this provider ?
    app.model.PcObject.check_and_save(vp)
    return jsonify(vp._asdict()), 200
