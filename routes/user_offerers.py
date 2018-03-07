from flask import current_app as app, jsonify, request

userOffererModel = app.model.UserOfferer

@app.route('/userOfferers', methods=['POST'])
def create_user_offerer():
    new_user_offerer = userOffererModel(from_dict=request.json)
    app.model.PcObject.check_and_save(new_user_offerer)
    return jsonify(new_user_offerer), 201
