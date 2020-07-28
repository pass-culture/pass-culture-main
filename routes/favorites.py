from flask import current_app as app
from flask import jsonify, request
from flask_login import current_user, login_required

from domain.favorites import create_favorite
from infrastructure.container import list_favorites_of_beneficiary
from models import FavoriteSQLEntity, Mediation, Offer
from repository import repository
from repository.favorite_queries import find_favorite_for_offer_and_user
from routes.serialization import as_dict
from routes.serialization.favorites_serialize import serialize_favorite, serialize_favorites
from utils.human_ids import dehumanize
from utils.rest import load_or_404
from validation.routes.offers import check_offer_id_is_present_in_request


@app.route('/favorites', methods=['POST'])
@login_required
def add_to_favorite():
    mediation = None
    offer_id = request.json.get('offerId')
    mediation_id = request.json.get('mediationId')
    check_offer_id_is_present_in_request(offer_id)

    offer = load_or_404(Offer, offer_id)
    if mediation_id is not None:
        mediation = load_or_404(Mediation, mediation_id)

    favorite = create_favorite(mediation, offer, current_user)
    repository.save(favorite)

    return jsonify(serialize_favorite(favorite, current_user)), 201


@app.route('/favorites/<offer_id>', methods=['DELETE'])
@login_required
def delete_favorite(offer_id):
    dehumanized_offer_id = dehumanize(offer_id)

    favorite = find_favorite_for_offer_and_user(dehumanized_offer_id, current_user.id) \
        .first_or_404()

    repository.delete(favorite)

    return jsonify(as_dict(favorite)), 200


@app.route('/favorites', methods=['GET'])
@login_required
def get_favorites():
    favorites = list_favorites_of_beneficiary.execute(current_user.id)

    return jsonify(serialize_favorites(favorites, current_user)), 200


@app.route('/favorites/<favorite_id>', methods=['GET'])
@login_required
def get_favorite(favorite_id):
    favorite = load_or_404(FavoriteSQLEntity, favorite_id)
    return jsonify(serialize_favorite(favorite, current_user)), 200
