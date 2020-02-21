from typing import List

from flask import current_app as app, jsonify, request
from flask_login import current_user, login_required

from domain.favorites import create_favorite
from domain.offers import find_first_matching_booking_from_offer_by_user
from models import Mediation, Offer, Favorite
from repository import repository
from repository.favorite_queries import find_favorite_for_offer_and_user, find_all_favorites_by_user_id
from routes.serialization import as_dict
from utils.human_ids import dehumanize
from utils.includes import FAVORITE_INCLUDES, \
    WEBAPP_GET_BOOKING_WITH_QR_CODE_INCLUDES
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

    return jsonify(_serialize_favorite(favorite)), 201


@app.route('/favorites/<offer_id>', methods=['DELETE'])
@login_required
def delete_favorite(offer_id):
    dehumanized_offer_id = dehumanize(offer_id)

    favorite = find_favorite_for_offer_and_user(dehumanized_offer_id,
                                                current_user.id) \
        .first_or_404()

    repository.delete(favorite)

    return jsonify(as_dict(favorite)), 200


@app.route('/favorites', methods=['GET'])
@login_required
def get_favorites():
    favorites = find_all_favorites_by_user_id(current_user.id)

    return jsonify(_serialize_favorites(favorites)), 200


@app.route('/favorites/<favorite_id>', methods=['GET'])
@login_required
def get_favorite(favorite_id):
    favorite = load_or_404(Favorite, favorite_id)
    return jsonify(_serialize_favorite(favorite)), 200


def _serialize_favorites(favorites: List[Favorite]) -> List:
    return list(map(_serialize_favorite, favorites))


def _serialize_favorite(favorite: Favorite) -> dict:
    dict_favorite = as_dict(favorite, includes=FAVORITE_INCLUDES)

    booking = find_first_matching_booking_from_offer_by_user(favorite.offer, current_user)
    if booking:
        dict_favorite['firstMatchingBooking'] = as_dict(
            booking, includes=WEBAPP_GET_BOOKING_WITH_QR_CODE_INCLUDES)

    return dict_favorite
