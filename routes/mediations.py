from flask import current_app as app, jsonify, request
from flask_login import current_user, login_required

mediationModel = app.model.Mediation

@app.route('/mediations', methods=['POST'])
@login_required
def create_mediation():
    new_mediation = mediationModel(from_dict=request.json)
    new_mediation.userId = current_user.get_id()
    app.model.PcObject.check_and_save(new_mediation)

    return jsonify(new_mediation), 201
