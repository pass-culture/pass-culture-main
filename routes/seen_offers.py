from flask import current_app as app, request
from flask_login import current_user, login_required

from models.feature import FeatureToggle
from use_cases.save_offer_seen_by_beneficiary import save_seen_offer
from utils.feature import feature_required
from utils.human_ids import dehumanize
from utils.rest import expect_json_data
from validation.routes.seen_offers import check_payload_is_valid


@app.route('/seen_offers', methods=['PUT'])
@feature_required(FeatureToggle.SAVE_SEEN_OFFERS)
@login_required
@expect_json_data
def put_seen_offers():
    payload = request.json
    check_payload_is_valid(payload)
    offer_id = dehumanize(payload['offerId'])
    save_seen_offer(current_user.id, offer_id)
    return '', 200
