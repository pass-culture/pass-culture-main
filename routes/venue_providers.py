import subprocess

from flask import current_app as app
from flask import jsonify, request
from flask_login import login_required

import local_providers
from domain.stock_provider.stock_provider_repository import StockProviderRepository
from infrastructure.container import api_fnac_stocks, api_libraires_stocks, api_titelive_stocks
from local_providers import FnacStocks, LibrairesStocks
from local_providers.titelive_stocks.titelive_stocks import TiteLiveStocks
from models.api_errors import ApiErrors
from models.venue_provider import VenueProvider
from repository.provider_queries import get_provider_enabled_for_pro_by_id
from routes.serialization import as_dict
from use_cases.connect_provider_to_venue import connect_provider_to_venue
from utils.config import API_ROOT_PATH
from utils.human_ids import dehumanize
from utils.includes import VENUE_PROVIDER_INCLUDES
from utils.rest import expect_json_data, load_or_404
from validation.routes.venue_providers import check_existing_provider, check_new_venue_provider_information


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
    check_new_venue_provider_information(venue_provider_payload)

    provider_id = dehumanize(venue_provider_payload['providerId'])
    provider = get_provider_enabled_for_pro_by_id(provider_id)
    check_existing_provider(provider)

    provider_class = getattr(local_providers, provider.localClass)
    stock_provider_repository_or_none = _get_stock_provider_repository(provider_class)
    new_venue_provider = connect_provider_to_venue(provider_class, stock_provider_repository_or_none,
                                                   venue_provider_payload)

    _run_first_synchronization(new_venue_provider)

    return jsonify(as_dict(new_venue_provider, includes=VENUE_PROVIDER_INCLUDES)), 201


def _get_stock_provider_repository(provider_class: object) -> StockProviderRepository:
    if provider_class == LibrairesStocks:
        return api_libraires_stocks
    elif provider_class == FnacStocks:
        return api_fnac_stocks
    elif provider_class == TiteLiveStocks:
        return api_titelive_stocks
    return None


def _run_first_synchronization(new_venue_provider: VenueProvider):
    subprocess.Popen('PYTHONPATH="." python scripts/pc.py update_providables'
                     + ' --venue-provider-id %s' % str(new_venue_provider.id),
                     shell=True,
                     cwd=API_ROOT_PATH)
