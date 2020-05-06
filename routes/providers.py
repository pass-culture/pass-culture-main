from flask import current_app as app, jsonify, request
from flask_login import login_required

from local_providers import AllocineStocks
from models import Venue
from repository.allocine_pivot_queries import has_allocine_pivot_for_venue
from repository.provider_queries import get_enabled_providers_for_pro, \
    get_providers_enabled_for_pro_excluding_specific_provider
from routes.serialization import as_dict
from utils.rest import load_or_404
from connectors import redis

from rq import Worker, Queue, Connection
from workers import worker
from workers.save_offerer_bank_informations import pc_synchronize_new_bank_informations


@app.route('/providers', methods=['GET'])
@login_required
def list_providers():
    providers = get_enabled_providers_for_pro()
    result = []
    for provider in providers:
        p_dict = as_dict(provider)
        del p_dict['apiKey']
        del p_dict['apiKeyGenerationDate']
        result.append(p_dict)
    return jsonify(result)


@app.route('/providers/<venue_id>', methods=['GET'])
@login_required
def get_providers_by_venue(venue_id: str):
    venue = load_or_404(Venue, venue_id)
    has_allocine_pivot = has_allocine_pivot_for_venue(venue)
    if has_allocine_pivot:
        providers = get_enabled_providers_for_pro()
    else:
        allocine_local_class = AllocineStocks.__name__
        providers = get_providers_enabled_for_pro_excluding_specific_provider(allocine_local_class)
    result = []
    for provider in providers:
        provider_dict = as_dict(provider)
        del provider_dict['apiKey']
        del provider_dict['apiKeyGenerationDate']
        result.append(provider_dict)
    return jsonify(result)


@app.route('/providers/<provider_name>/application_update', methods=['POST'])
def post_update_demarches_simplifiees_application(provider_name: str):
    try:
        application_id = request.form['dossier_id']
    except:
        return '', 400
    worker.redis_queue.enqueue_call(func=pc_synchronize_new_bank_informations, args=(application_id, ))
    return '', 202
