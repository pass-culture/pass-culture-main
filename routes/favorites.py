from typing import List

from domain.favorites import create_favorite
from models import Mediation, Offer, PcObject, Favorite
from models.feature import FeatureToggle
from repository.favorite_queries import find_favorite_for_offer_mediation_and_user, find_all_favorites_by_user_id
from utils.feature import feature_required
from flask import current_app as app, jsonify, request
from flask_login import current_user, login_required

from utils.human_ids import dehumanize
from utils.includes import FAVORITE_INCLUDES
from utils.rest import load_or_404
from validation.offers import check_offer_id_and_mediation_id_are_present_in_request


@app.route('/favorites', methods=['POST'])
@feature_required(FeatureToggle.FAVORITE_OFFER)
@login_required
def add_to_favorite():
    offer_id = request.json.get('offerId')
    mediation_id = request.json.get('mediationId')
    check_offer_id_and_mediation_id_are_present_in_request(offer_id, mediation_id)

    offer = load_or_404(Offer, offer_id)
    mediation = load_or_404(Mediation, mediation_id)

    favorite = create_favorite(mediation, offer, current_user)
    PcObject.save(favorite)

    return jsonify(favorite.as_dict()), 201


@app.route('/favorites/<offer_id>/<mediation_id>', methods=['DELETE'])
@feature_required(FeatureToggle.FAVORITE_OFFER)
@login_required
def delete_favorite(offer_id, mediation_id):
    dehumanized_offer_id = dehumanize(offer_id)
    dehumanized_mediation_id = dehumanize(mediation_id)

    favorite = find_favorite_for_offer_mediation_and_user(dehumanized_mediation_id,
                                                          dehumanized_offer_id,
                                                          current_user.id) \
        .first_or_404()

    PcObject.delete(favorite)

    return jsonify({}), 204


@app.route('/favorites', methods=['GET'])
@feature_required(FeatureToggle.FAVORITE_OFFER)
@login_required
def get_favorites():
    favorites = find_all_favorites_by_user_id(current_user.id)

    return jsonify(_serialize_favorites(favorites)), 200


def _serialize_favorites(favorites: List[Favorite]) -> List:
    return list(map(_serialize_favorite, favorites))


def _serialize_favorite(favorite: Favorite) -> dict:
    return favorite.as_dict(include=FAVORITE_INCLUDES)
