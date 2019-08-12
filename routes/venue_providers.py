""" venue providers """
import subprocess

from flask import current_app as app, jsonify, request

from models.api_errors import ApiErrors
from models.pc_object import PcObject
from models.provider import Provider
from models.user_offerer import RightsType
from models.venue_provider import VenueProvider
from repository.venue_provider_queries import find_venue_provider
from routes.serialization import as_dict
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
        e.add_error('venueId', 'Vous devez obligatoirement fournir le paramètre venueId')
        return jsonify(e.errors), 400

    vp_query = VenueProvider.query\
                            .filter_by(venueId=dehumanize(venueId))
    return jsonify([
        as_dict(venue_provider, include=VENUE_PROVIDER_INCLUDES)
        for venue_provider in vp_query.all()
    ])


@app.route('/venueProviders/<id>', methods=['GET'])
@login_or_api_key_required
def get_venue_provider(id):
    venue_provider = load_or_404(VenueProvider, id)
    return jsonify(as_dict(venue_provider, include=VENUE_PROVIDER_INCLUDES))


@app.route('/venueProviders', methods=['POST'])
@login_or_api_key_required
@expect_json_data
def create_venue_provider():
    new_venue_provider = VenueProvider(from_dict=request.json)

    provider = load_or_404(Provider, request.json['providerId'])
    is_provider_available_for_pro_usage = provider.isActive and provider.enabledForPro
    if not is_provider_available_for_pro_usage:
        errors = ApiErrors()
        errors.status_code = 401
        errors.add_error('localClass', "Ce fournisseur n'est pas activé")
        errors.maybe_raise()

    is_existing_venue_provider = find_venue_provider(provider.id,
                                                  dehumanize(request.json['venueId']),
                                                  request.json['venueIdAtOfferProvider'])
    if is_existing_venue_provider:
        errors = ApiErrors()
        errors.status_code = 401
        errors.add_error('venueIdAtOfferProvider', "Il y a déjà un fournisseur pour votre identifiant")
        errors.maybe_raise()

    PcObject.save(new_venue_provider)

    subprocess.Popen('PYTHONPATH="." python scripts/pc.py update_providables'
                     + ' --venue-provider-id %s' % str(new_venue_provider.id),
                     shell=True,
                     cwd=API_ROOT_PATH)

    return jsonify(as_dict(new_venue_provider, include=VENUE_PROVIDER_INCLUDES)), 201


@app.route('/venueProviders/<id>', methods=['PATCH'])
@login_or_api_key_required
@expect_json_data
def edit_venue_provider(id):
    venue_provider = load_or_404(VenueProvider, id)
    venue_provider.populate_from_dict(request.json)
    PcObject.save(venue_provider)
    return jsonify(as_dict(venue_provider, include=VENUE_PROVIDER_INCLUDES)), 200


@app.route('/venueProviders/<id>', methods=['DELETE'])
@login_or_api_key_required
def delete_venue_provider(id):
    venue_provider = load_or_404(VenueProvider, id)
    ensure_current_user_has_rights(RightsType.editor,
                                   venue_provider.venue.managingOffererId)
    # TODO: should we also delete all the associated products...?
    return delete(venue_provider)
