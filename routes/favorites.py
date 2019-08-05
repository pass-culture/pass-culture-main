from typing import List

from domain.favorites import create_favorite
from models import Mediation, Offer, PcObject, Favorite
from models.feature import FeatureToggle
from repository.favorite_queries import find_favorite_for_offer_mediation_and_user, find_all_favorites_by_user_id
from utils.feature import feature_required
from flask import current_app as app, jsonify, request
from flask_login import current_user, login_required

from domain.favorites import find_first_matching_booking_from_favorite
from repository.booking_queries import find_bookings_from_recommendation
from validation.offers import check_offer_id_and_mediation_id_are_present_in_request
from utils.human_ids import dehumanize
from utils.includes import FAVORITE_INCLUDES, \
                           RECOMMENDATION_INCLUDES, \
                           WEBAPP_GET_BOOKING_INCLUDES
from utils.rest import load_or_404


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

    return jsonify(_serialize_favorite(favorite)), 201

@app.route('/favorites/<offer_id>', methods=['DELETE'])
@app.route('/favorites/<offer_id>/<mediation_id>', methods=['DELETE'])
@feature_required(FeatureToggle.FAVORITE_OFFER)
@login_required
def delete_favorite(offer_id, mediation_id=None):
    dehumanized_offer_id = dehumanize(offer_id)
    dehumanized_mediation_id = dehumanize(mediation_id)

    favorite = find_favorite_for_offer_mediation_and_user(dehumanized_mediation_id,
                                                          dehumanized_offer_id,
                                                          current_user.id) \
        .first_or_404()
    favorite_id = favorite.id

    PcObject.delete(favorite)

    return jsonify(favorite.as_dict()), 200


@app.route('/favorites', methods=['GET'])
@feature_required(FeatureToggle.FAVORITE_OFFER)
@login_required
def get_favorites():
    favorites = find_all_favorites_by_user_id(current_user.id)

    return jsonify(_serialize_favorites(favorites)), 200


@app.route('/favorites/<favorite_id>', methods=['GET'])
@feature_required(FeatureToggle.FAVORITE_OFFER)
@login_required
def get_favorite(favorite_id):
    favorite = load_or_404(Favorite, favorite_id)
    return jsonify(_serialize_favorite(favorite)), 200


def _serialize_favorites(favorites: List[Favorite]) -> List:
    return list(map(_serialize_favorite, favorites))


def _serialize_favorite(favorite: Favorite) -> dict:
    dict_favorite = favorite.as_dict(include=FAVORITE_INCLUDES)

    first_matching_booking = find_first_matching_booking_from_favorite(favorite, current_user)
    if first_matching_booking:
        dict_favorite['firstMatchingBooking'] = _serialize_booking(first_matching_booking)

    return dict_favorite

def _serialize_booking(booking):
    return booking.as_dict(include=WEBAPP_GET_BOOKING_INCLUDES)
