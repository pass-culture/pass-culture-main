""" mediations """
from flask import current_app as app, jsonify, request
from flask_login import current_user, login_required

from utils.human_ids import dehumanize
from utils.rest import delete, ensure_current_user_has_rights, load_or_404

Mediation = app.model.Mediation
RightsType = app.model.RightsType


@app.route('/mediations', methods=['POST'])
@login_required
def create_mediation():
    new_mediation = Mediation()
    new_mediation.author = current_user
    new_mediation.eventId = dehumanize(request.json['eventId'])
    new_mediation.offererId = dehumanize(request.json['offererId'])
    app.model.PcObject.check_and_save(new_mediation)
    return jsonify(new_mediation), 201


@app.route('/mediations/<id>', methods=['DELETE'])
@login_required
def delete_mediation(id):
    mediation = load_or_404(Mediation, id)
    ensure_current_user_has_rights(RightsType.editor,
                                   mediation.offererId)
    return delete(mediation)
