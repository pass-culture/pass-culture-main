from flask import current_app as app, request
from flask_login import login_required

from use_cases.save_offer_seen_by_beneficiary import save_seen_offer
from utils.human_ids import dehumanize
from utils.rest import expect_json_data
from validation.routes.seen_offers import check_payload_is_valid


@app.route('/seen_offers', methods=['PUT'])
@login_required
@expect_json_data
def put_seen_offers():
    payload = request.json
    check_payload_is_valid(payload)
    user_id = dehumanize(payload['userId'])
    offer_id = dehumanize(payload['offerId'])
    save_seen_offer(user_id, offer_id)
    return '', 200
