""" mediations """
from flask import current_app as app, jsonify, request
from flask_login import current_user, login_required

from utils.human_ids import dehumanize


@app.route('/mediations', methods=['POST'])
@login_required
def create_mediation():
    new_mediation = app.model.Mediation()
    print('request.json', request.json)
    new_mediation.author = current_user
    new_mediation.eventId = dehumanize(request.json['eventId'])
    new_mediation.offererId = dehumanize(request.json['offererId'])
    app.model.PcObject.check_and_save(new_mediation)
    return jsonify(new_mediation), 201
