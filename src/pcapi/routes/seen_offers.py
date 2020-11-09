from flask import request
from flask_login import current_user
from flask_login import login_required

from pcapi.flask_app import private_api
from pcapi.models.feature import FeatureToggle
from pcapi.use_cases.save_offer_seen_by_beneficiary import save_seen_offer
from pcapi.utils.feature import feature_required
from pcapi.utils.human_ids import dehumanize
from pcapi.utils.rest import expect_json_data
from pcapi.validation.routes.seen_offers import check_payload_is_valid


@private_api.route('/seen_offers', methods=['PUT'])
@feature_required(FeatureToggle.SAVE_SEEN_OFFERS)
@login_required
@expect_json_data
def put_seen_offers():
    payload = request.json
    check_payload_is_valid(payload)
    offer_id = dehumanize(payload['offerId'])
    save_seen_offer(current_user.id, offer_id)
    return '', 200
