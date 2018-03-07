from base64 import b64decode
from flask import current_app as app, jsonify, request
from flask_login import current_user, login_required, logout_user

from utils.human_ids import humanize
from utils.object_storage import store_public_object

include_joins = [
    {
        "key": 'userOfferers',
        "resolve": (lambda element, filters: element['offerer']),
        "sub_joins": ['offerer']
    }
]
userModel = app.model.User

@login_required
@app.route("/users/me", methods=["GET"])
def get_profile():
    if current_user.is_authenticated:
        user = current_user._asdict(include_joins=include_joins)
        return jsonify(user), 200
    return jsonify({"message": "no current user"}), 401

@app.route("/users/signin", methods=["POST"])
def signin():
    json = request.get_json()
    identifier = json.get("identifier")
    password = json.get("password")
    # special auth defined in utils/login_manager
    # that is also used for now for api outside browser requests
    user = app.get_user_with_credentials(identifier, password)
    if not isinstance(user, dict):
        user = user._asdict(include_joins=include_joins)
    error = user.get('error')
    return jsonify(user), error or 200;

@login_required
@app.route("/users/signout", methods=["GET"])
def signout():
    logout_user()
    return jsonify({ "text": "Logged out" })

@app.route("/users/signup", methods=["POST"])
def signup():
    new_user = userModel(from_dict=request.json)
    if (userModel.query.filter_by(email=new_user.email).count())>0:
        return jsonify({"message": "Already an account with this email"}), 400;
    new_user.id = None
    app.model.PcObject.check_and_save(new_user)
    # thumb
    if 'thumb_content' in request.json:
        store_public_object(
            "thumbs",
            "users/"+humanize(new_user.id),
            b64decode(request.json['thumb_content']),
            request.json['thumb_content_type']
        )
    return jsonify(new_user._asdict(include_joins=include_joins)), 201;
