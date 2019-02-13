""" user offerers """
from flask import current_app as app, jsonify, request
from flask_login import current_user, login_required

from models.pc_object import PcObject
from models.user_offerer import UserOfferer
from utils.human_ids import dehumanize

@app.route('/userOfferers/<offererId>', methods=['GET'])
@login_required
def get_user_offerer(offererId):
    user_offerer = UserOfferer.query.filter_by(
        user=current_user,
        offererId=dehumanize(offererId)
    )
    return jsonify(user_offerer), 200


@app.route('/userOfferers', methods=['POST'])
@login_required
def create_user_offerer():
    new_user_offerer = UserOfferer(from_dict=request.json)
    PcObject.check_and_save(new_user_offerer)
    return jsonify(new_user_offerer), 201
