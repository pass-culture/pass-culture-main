from flask import jsonify
from flask_login import current_user
from flask_login import login_required

from pcapi.flask_app import private_api
from pcapi.models.user_offerer import UserOfferer
from pcapi.routes.serialization import as_dict
from pcapi.utils.human_ids import dehumanize
from pcapi.utils.includes import USER_OFFERER_INCLUDES


@private_api.route("/userOfferers/<offerer_id>", methods=["GET"])
@login_required
def get_user_offerer(offerer_id):
    user_offerers = UserOfferer.query.filter_by(user=current_user, offererId=dehumanize(offerer_id)).all()
    return jsonify([as_dict(user_offerer, includes=USER_OFFERER_INCLUDES) for user_offerer in user_offerers]), 200
