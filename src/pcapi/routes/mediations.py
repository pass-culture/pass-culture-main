from flask import current_app as app
from flask import jsonify
from flask import request
from flask_login import current_user
from flask_login import login_required

from pcapi.connectors import redis
from pcapi.connectors.thumb_storage import create_thumb
from pcapi.connectors.thumb_storage import read_thumb
from pcapi.flask_app import private_api
from pcapi.models.feature import FeatureToggle
from pcapi.models.mediation_sql_entity import MediationSQLEntity
from pcapi.models.user_offerer import RightsType
from pcapi.repository import feature_queries
from pcapi.repository import repository
from pcapi.routes.serialization import as_dict
from pcapi.utils.human_ids import dehumanize
from pcapi.utils.includes import MEDIATION_INCLUDES
from pcapi.utils.rest import ensure_current_user_has_rights
from pcapi.utils.rest import expect_json_data
from pcapi.utils.rest import load_or_404
from pcapi.validation.routes.mediations import check_thumb_in_request
from pcapi.validation.routes.mediations import check_thumb_quality


@private_api.route("/mediations", methods=["POST"])
@login_required
def create_mediation():
    check_thumb_in_request(files=request.files, form=request.form)
    offerer_id = dehumanize(request.form["offererId"])
    offer_id = dehumanize(request.form["offerId"])
    credit = request.form.get("credit")
    ensure_current_user_has_rights(RightsType.editor, offerer_id)
    mediation = MediationSQLEntity()
    mediation.author = current_user
    mediation.offerId = offer_id
    mediation.credit = credit
    mediation.offererId = offerer_id
    thumb = read_thumb(files=request.files, form=request.form)
    check_thumb_quality(thumb)
    repository.save(mediation)
    mediation = create_thumb(mediation, thumb, 0, crop=_get_crop(request.form))
    repository.save(mediation)
    if feature_queries.is_active(FeatureToggle.SYNCHRONIZE_ALGOLIA):
        redis.add_offer_id(client=app.redis_client, offer_id=offer_id)
    return jsonify(as_dict(mediation)), 201


@private_api.route("/mediations/<mediation_id>", methods=["GET"])
@login_required
def get_mediation(mediation_id):
    mediation = load_or_404(MediationSQLEntity, mediation_id)
    return jsonify(as_dict(mediation))


@private_api.route("/mediations/<mediation_id>", methods=["PATCH"])
@login_required
@expect_json_data
def update_mediation(mediation_id):
    mediation = load_or_404(MediationSQLEntity, mediation_id)
    ensure_current_user_has_rights(RightsType.editor, mediation.offer.venue.managingOffererId)
    mediation = MediationSQLEntity.query.filter_by(id=dehumanize(mediation_id)).first()
    data = request.json
    mediation.populate_from_dict(data)
    repository.save(mediation)
    if feature_queries.is_active(FeatureToggle.SYNCHRONIZE_ALGOLIA):
        redis.add_offer_id(client=app.redis_client, offer_id=mediation.offerId)
    return jsonify(as_dict(mediation, includes=MEDIATION_INCLUDES)), 200


def _get_crop(form):
    if "croppingRect[x]" in form and "croppingRect[y]" in form and "croppingRect[height]" in form:
        return [float(form["croppingRect[x]"]), float(form["croppingRect[y]"]), float(form["croppingRect[height]"])]
