""" user offerers """
from flask import current_app as app, jsonify, request
from flask_login import login_required

from models.pc_object import PcObject
from models.user_offerer import UserOfferer


@app.route('/userOfferers', methods=['POST'])
@login_required
def create_user_offerer():
    new_user_offerer = UserOfferer(from_dict=request.json)
    PcObject.check_and_save(new_user_offerer)
    return jsonify(new_user_offerer), 201
