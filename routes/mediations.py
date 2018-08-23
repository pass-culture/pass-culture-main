""" mediations """
from flask import current_app as app, jsonify, request
from flask_login import current_user, login_required

from models.api_errors import ApiErrors
from models.mediation import Mediation
from models.pc_object import PcObject
from models.user_offerer import RightsType
from utils.human_ids import dehumanize
from utils.rest import ensure_current_user_has_rights, load_or_404

ALLOWED_EXTENSIONS = set(['jpg', 'png', 'jpeg', 'gif'])


@app.route('/mediations', methods=['POST'])
@login_required
def create_mediation():
    # TODO: Allow to receive a URL from request.form['thumb']
    # save_thumb already does it so it should be easy, but I can't make it ...
    if 'thumb' not in request.files \
            or request.files['thumb'].filename == '':
        e = ApiErrors()
        e.addError('thumb', "Vous devez fournir une image d'accroche")
        return jsonify(e.errors), 400

    thumb = request.files['thumb']
    filename_parts = thumb.filename.rsplit('.', 1)
    if len(filename_parts) < 2 \
            or filename_parts[1].lower() not in ALLOWED_EXTENSIONS:
        e = ApiErrors()
        e.addError('thumb', "Ce format d'image n'est pas autorisé")
        return jsonify(e.errors), 400

    offerer_id = dehumanize(request.form['offererId'])
    ensure_current_user_has_rights(RightsType.editor, offerer_id)

    new_mediation = Mediation()
    new_mediation.author = current_user
    new_mediation.offerId = dehumanize(request.form['offerId'])
    new_mediation.credit = request.form.get('credit')
    new_mediation.offererId = offerer_id
    PcObject.check_and_save(new_mediation)

    if 'croppingRect[x]' in request.form:
        crop = [float(request.form['croppingRect[x]']),
                float(request.form['croppingRect[y]']),
                float(request.form['croppingRect[height]'])]
    else:
        crop = None

    new_mediation.save_thumb(thumb.read(), 0, crop=crop)

    return jsonify(new_mediation), 201


@app.route('/mediations/<mediation_id>', methods=['GET'])
@login_required
def get_mediation(mediation_id):
    mediation = load_or_404(Mediation, mediation_id)
    return jsonify(mediation._asdict())


@app.route('/mediations/<mediation_id>', methods=['PATCH'])
@login_required
def update_mediation(mediation_id):
    mediation = load_or_404(Mediation, mediation_id)
    ensure_current_user_has_rights(RightsType.editor, mediation.offer.venue.managingOffererId)
    mediation = Mediation.query.filter_by(id=dehumanize(mediation_id)).first()
    mediation.populateFromDict(request.json)
    PcObject.check_and_save(mediation)
    return jsonify(mediation._asdict()), 200
