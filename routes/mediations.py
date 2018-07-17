from models.mediation import Mediation
from models.pc_object import PcObject

""" mediations """
from flask import current_app as app, jsonify, request
from flask_login import current_user, login_required

from models.api_errors import ApiErrors
from utils.human_ids import dehumanize
from utils.rest import delete, ensure_current_user_has_rights, load_or_404

Mediation = Mediation
RightsType = RightsType

ALLOWED_EXTENSIONS = set(['jpg', 'png', 'jpeg', 'gif'])


@app.route('/mediations', methods=['POST'])
@login_required
def create_mediation():
    # TODO: Allow to receive a URL from request.form['thumb']
    # save_thumb already does it so it should be easy, but I can't make it ...

    if 'thumb' not in request.files\
       or request.files['thumb'].filename == '':
        e = ApiErrors()
        e.addError('thumb', "Vous devez fournir une image d'accroche")
        return jsonify(e.errors), 400

    thumb = request.files['thumb']
    filename_parts = thumb.filename.rsplit('.', 1)
    if len(filename_parts)<2\
       or filename_parts[1].lower() not in ALLOWED_EXTENSIONS:
        e = ApiErrors()
        e.addError('thumb', "Ce format d'image n'est pas autorisé")
        return jsonify(e.errors), 400

    offererId = dehumanize(request.form['offererId'])
    ensure_current_user_has_rights(RightsType.editor,
                                   offererId)

    new_mediation = Mediation()
    new_mediation.author = current_user
    new_mediation.eventId = dehumanize(request.form['eventId'])
    new_mediation.offererId = offererId
    PcObject.check_and_save(new_mediation)

    if 'croppingRect[x]' in request.form:
        crop = [float(request.form['croppingRect[x]']),
                float(request.form['croppingRect[y]']),
                float(request.form['croppingRect[height]'])]
    else:
        crop = None

    new_mediation.save_thumb(thumb.read(), 0, crop=crop)

    return jsonify(new_mediation), 201


@app.route('/mediations/<id>', methods=['GET'])
@login_required
def get_mediation(id):
    mediation = load_or_404(Mediation, id)
    return jsonify(mediation._asdict())


@app.route('/mediations/<id>', methods=['DELETE'])
@login_required
def delete_mediation(id):
    mediation = load_or_404(Mediation, id)
    ensure_current_user_has_rights(RightsType.editor,
                                   mediation.offererId)
    return delete(mediation)
