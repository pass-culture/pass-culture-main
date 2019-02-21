""" venue providers """
import subprocess
from flask import current_app as app, jsonify, request

from models.api_errors import ApiErrors
from models.pc_object import PcObject
from models.provider import Provider
from models.user_offerer import RightsType
from models.venue_provider import VenueProvider
from utils.config import API_ROOT_PATH
from utils.human_ids import dehumanize
from utils.includes import VENUE_PROVIDER_INCLUDES
from utils.rest import delete, expect_json_data, \
    ensure_current_user_has_rights, \
    load_or_404, \
    login_or_api_key_required


@app.route('/venueProviders', methods=['GET'])
@login_or_api_key_required
def list_venue_providers():
    venueId = request.args.get('venueId')
    if venueId is None:
        e = ApiErrors()
        e.addError('venueId', 'Vous devez obligatoirement fournir le paramètre venueId')
        return jsonify(e.errors), 400

    vp_query = VenueProvider.query\
                            .filter_by(venueId=dehumanize(venueId))
    return jsonify([
        vp._asdict(include=VENUE_PROVIDER_INCLUDES)
        for vp in vp_query.all()
    ])


@app.route('/venueProviders/<id>', methods=['GET'])
@login_or_api_key_required
def get_venue_provider(id):
    vp = load_or_404(VenueProvider, id)
    return jsonify(vp._asdict(include=VENUE_PROVIDER_INCLUDES))


@app.route('/venueProviders', methods=['POST'])
@login_or_api_key_required
@expect_json_data
def create_venue_provider():
    new_vp = VenueProvider(from_dict=request.json)

    # CHECK THAT THIS PROVIDER IS ACTIVE
    provider = load_or_404(Provider, request.json['providerId'])
    if not provider.isActive:
        errors = ApiErrors()
        errors.status_code = 401
        errors.addError('localClass', "Ce fournisseur n' est pas activé")
        errors.maybeRaise()
        return

    # CHECK THAT THERE IS NOT ALREADY A VENUE PROVIDER
    # FOR THE SAME VENUE, PROVIDER, IDENTIFIER
    same_venue_provider = VenueProvider.query.filter_by(
        providerId=provider.id,
        venueId=dehumanize(request.json['venueId']),
        venueIdAtOfferProvider=request.json['venueIdAtOfferProvider']
    ).first()
    if same_venue_provider:
        errors = ApiErrors()
        errors.status_code = 401
        errors.addError('venueIdAtOfferProvider', "Il y a déjà un fournisseur pour votre identifiant")
        errors.maybeRaise()

    # SAVE
    PcObject.check_and_save(new_vp)

    # CALL THE PROVIDER SUB PROCESS
    p = subprocess.Popen('PYTHONPATH="." python scripts/pc.py update_providables'
                         + ' --venue_provider_id %s' % str(new_vp.id),
                         #stdout=subprocess.PIPE,
                         #stderr=subprocess.PIPE,
                         shell=True,
                         cwd=API_ROOT_PATH)
    #out, err = p.communicate()
    #print("STDOUT:", out)
    #print("STDERR:", err)

    # RETURN
    return jsonify(new_vp._asdict(include=VENUE_PROVIDER_INCLUDES)), 201


@app.route('/venueProviders/<id>', methods=['PATCH'])
@login_or_api_key_required
@expect_json_data
def edit_venue_provider(id):
    vp = load_or_404(VenueProvider, id)
    vp.populateFromDict(request.json)
    PcObject.check_and_save(vp)
    return jsonify(vp._asdict()), 200


@app.route('/venueProviders/<id>', methods=['DELETE'])
@login_or_api_key_required
def delete_venue_provider(id):
    vp = load_or_404(VenueProvider, id)
    ensure_current_user_has_rights(RightsType.editor,
                                   vp.venue.managingOffererId)
    # TODO: should we also delete all the associated events/things...?
    return delete(vp)
