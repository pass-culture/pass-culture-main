import subprocess
from typing import Dict

from flask import current_app as app, jsonify, request
from flask_login import login_required

import local_providers
from local_providers import AllocineStocks, TiteLiveStocks, LibrairesStocks
from models import Venue
from models.api_errors import ApiErrors
from models.venue_provider import VenueProvider
from repository import repository
from repository.allocine_pivot_queries import get_allocine_theaterId_for_venue
from repository.provider_queries import get_provider_enabled_for_pro_by_id
from repository.venue_provider_price_rule_queries import save_venue_provider_price_rule
from routes.serialization import as_dict
from utils.config import API_ROOT_PATH
from utils.human_ids import dehumanize
from utils.includes import VENUE_PROVIDER_INCLUDES
from utils.rest import expect_json_data, \
    load_or_404
from validation.routes.venue_providers import validate_new_venue_provider_information, validate_existing_provider


@app.route('/venueProviders', methods=['GET'])
@login_required
def list_venue_providers():
    venue_id = request.args.get('venueId')
    if venue_id is None:
        e = ApiErrors()
        e.add_error('venueId', 'Vous devez obligatoirement fournir le paramètre venueId')
        return jsonify(e.errors), 400

    vp_query = VenueProvider.query \
        .filter_by(venueId=dehumanize(venue_id))
    return jsonify([
        as_dict(venue_provider, includes=VENUE_PROVIDER_INCLUDES)
        for venue_provider in vp_query.all()
    ])


@app.route('/venueProviders/<id>', methods=['GET'])
@login_required
def get_venue_provider(id):
    venue_provider = load_or_404(VenueProvider, id)
    return jsonify(as_dict(venue_provider, includes=VENUE_PROVIDER_INCLUDES))


@app.route('/venueProviders', methods=['POST'])
@login_required
@expect_json_data
def create_venue_provider():
    venue_provider_payload = request.json
    validate_new_venue_provider_information(venue_provider_payload)

    provider_id = dehumanize(venue_provider_payload['providerId'])
    provider = get_provider_enabled_for_pro_by_id(provider_id)
    validate_existing_provider(provider)

    provider_type = getattr(local_providers, provider.localClass)
    if provider_type == AllocineStocks:
        new_venue_provider = _save_allocine_venue_provider(venue_provider_payload)
    elif provider_type == LibrairesStocks or TiteLiveStocks:
        new_venue_provider = _save_titelive_or_libraires_venue_provider(venue_provider_payload)

    _run_first_synchronization(new_venue_provider)

    return jsonify(as_dict(new_venue_provider, includes=VENUE_PROVIDER_INCLUDES)), 201


def _run_first_synchronization(new_venue_provider):
    subprocess.Popen('PYTHONPATH="." python scripts/pc.py update_providables'
                     + ' --venue-provider-id %s' % str(new_venue_provider.id),
                     shell=True,
                     cwd=API_ROOT_PATH)


def _save_allocine_venue_provider(payload: Dict) -> VenueProvider:
    venue = load_or_404(Venue, payload['venueId'])
    allocine_theater_id = get_allocine_theaterId_for_venue(venue)

    venue_provider = VenueProvider()
    venue_provider.venueId = venue.id
    venue_provider.providerId = dehumanize(payload['providerId'])
    venue_provider.venueIdAtOfferProvider = allocine_theater_id

    save_venue_provider_price_rule(venue_provider, payload.get('price'))

    repository.save(venue_provider)
    return venue_provider


def _save_titelive_or_libraires_venue_provider(payload: Dict) -> VenueProvider:
    venue = load_or_404(Venue, payload['venueId'])
    venue_provider = VenueProvider()
    venue_provider.venueId = venue.id
    venue_provider.providerId = dehumanize(payload['providerId'])
    venue_provider.venueIdAtOfferProvider = venue.siret

    repository.save(venue_provider)
    return venue_provider
