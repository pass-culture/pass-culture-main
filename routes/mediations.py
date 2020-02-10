from flask import current_app as app, jsonify, request
from flask_login import current_user, login_required

from connectors import redis
from connectors.thumb_storage import read_thumb, create_thumb
from domain.mediations import create_new_mediation
from models.mediation import Mediation
from models.user_offerer import RightsType
from repository import repository
from routes.serialization import as_dict
from utils.human_ids import dehumanize
from utils.includes import MEDIATION_INCLUDES
from utils.rest import ensure_current_user_has_rights, load_or_404, expect_json_data
from validation.routes.mediations import check_thumb_in_request, check_thumb_quality


@app.route('/mediations', methods=['POST'])
@login_required
def create_mediation():
    check_thumb_in_request(files=request.files, form=request.form)
    offerer_id = dehumanize(request.form['offererId'])
    offer_id = dehumanize(request.form['offerId'])
    credit = request.form.get('credit')
    ensure_current_user_has_rights(RightsType.editor, offerer_id)
    mediation = create_new_mediation(offer_id, offerer_id, current_user, credit)
    thumb = read_thumb(files=request.files, form=request.form)
    check_thumb_quality(thumb)
    repository.save(mediation)
    mediation = create_thumb(mediation, thumb, 0, crop=_get_crop(request.form))
    repository.save(mediation)
    redis.add_offer_id(client=app.redis_client, offer_id=offer_id)
    return jsonify(as_dict(mediation)), 201


@app.route('/mediations/<mediation_id>', methods=['GET'])
@login_required
def get_mediation(mediation_id):
    mediation = load_or_404(Mediation, mediation_id)
    return jsonify(as_dict(mediation))


@app.route('/mediations/<mediation_id>', methods=['PATCH'])
@login_required
@expect_json_data
def update_mediation(mediation_id):
    mediation = load_or_404(Mediation, mediation_id)
    ensure_current_user_has_rights(RightsType.editor, mediation.offer.venue.managingOffererId)
    mediation = Mediation.query.filter_by(id=dehumanize(mediation_id)).first()
    data = request.json
    mediation.populate_from_dict(data)
    repository.save(mediation)
    redis.add_offer_id(client=app.redis_client, offer_id=mediation.offerId)
    return jsonify(as_dict(mediation, includes=MEDIATION_INCLUDES)), 200


def _get_crop(form):
    if 'croppingRect[x]' in form \
            and 'croppingRect[y]' in form \
            and 'croppingRect[height]' in form:
        return [
            float(form['croppingRect[x]']),
            float(form['croppingRect[y]']),
            float(form['croppingRect[height]'])
        ]
