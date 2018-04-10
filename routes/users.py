"""users routes"""
from base64 import b64decode
from flask import current_app as app, jsonify, request
from flask_login import current_user, login_required, logout_user, login_user

from models.api_errors import ApiErrors
from utils.human_ids import humanize
from utils.object_storage import store_public_object

user_include = ['offerers', '-password']
User = app.model.User


def make_user_query():
    query = User.query
    return query


@app.route("/users/me", methods=["GET"])
@login_required
def get_profile():
    return jsonify(current_user._asdict(include=user_include))


@app.route("/users/signin", methods=["POST"])
def signin():
    json = request.get_json()
    identifier = json.get("identifier")
    password = json.get("password")
    user = app.get_user_with_credentials(identifier, password)
    return jsonify(user._asdict(include=user_include)), 200


@app.route("/users/signout", methods=["GET"])
@login_required
def signout():
    logout_user()
    return jsonify({"global": "Deconnecté"})


@app.route("/users", methods=["POST"])
def signup():
    if 'contact_ok' not in request.json or\
       (request.json['contact_ok'] is not True and
        str(request.json['contact_ok']).lower() != 'true'):
        e = ApiErrors()
        e.addError('contact_ok', 'Vous devez obligatoirement cocher cette case')
        return jsonify(e.errors), 400

    new_user = User(from_dict=request.json)
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
    login_user(new_user)
    return jsonify(new_user._asdict(include=user_include)), 201
