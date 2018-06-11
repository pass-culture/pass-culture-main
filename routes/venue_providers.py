""" venues """
from flask import current_app as app, jsonify, request

from utils.human_ids import dehumanize
from utils.includes import VENUE_PROVIDER_INCLUDES
from utils.rest import expect_json_data

@app.route('/venueProviders/<venueId>', methods=['GET'])
def list_venue_providers(venueId):
    venue_providers = app.model.VenueProvider\
                         .query.filter_by(
                             venueId=dehumanize(venueId))
    return jsonify([
        vp._asdict(include=VENUE_PROVIDER_INCLUDES)
        for vp in venue_providers
    ])

@app.route('/venueProviders', methods=['POST'])
@expect_json_data
def create_venue_provider():
    new_vp = app.model.VenueProvider(from_dict=request.json)
    #TODO: check that provider is active
    app.model.PcObject.check_and_save(new_vp)
#    subprocess.Popen(['pc', 'update_providables', '-p', new_vp.provider.name,
#                                                  '-v', new_vp.venueId],
#                     cwd=Path(path.dirname(path.realpath(__file__))) / '..')
    return jsonify(new_vp._asdict(include=VENUE_PROVIDER_INCLUDES)), 201


@app.route('/venue_providers/<venueId>/<providerId>/<venueIdAtOfferProvider>', methods=['PATCH'])
@expect_json_data
def edit_venue_provider(venueId, providerId, venueIdAtOfferProvider):
    vp = VenueProvider.query.filter_by(venueId=dehumanize(venueId),
                                       providerId=dehumanize(providerId),
                                       venueIdAtOfferProvider=dehumanize(venueIdAtOfferProvider))\
                      .first_or_404()
    update(vp, request.json)
    #TODO: remove things from this provider ?
    vp.venueId = dehumanize(venueId)
    app.model.PcObject.check_and_save(vp)
    return jsonify(vp._asdict()), 200


@app.route('/venueProviders/<id>', methods=['DELETE'])
@expect_json_data
def delete_venue_provider(id):
    app.model.VenueProvider.query.filter_by(
        id=dehumanize(id)
    ).delete()
    return jsonify({'text': "Deletion was successful!"}), 200
