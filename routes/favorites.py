from domain.favorites import create_favorite
from models import Mediation, Offer, PcObject
from models.feature import FeatureToggle
from repository.favorite_queries import find_favorite_for_offer_mediation_and_user
from utils.feature import feature_required
from flask import current_app as app, jsonify, request
from flask_login import current_user, login_required

from utils.human_ids import dehumanize
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
