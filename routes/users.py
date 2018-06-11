"""users routes"""
from os import path
from pathlib import Path
from flask import current_app as app, jsonify, request
from flask_login import current_user, login_required, logout_user, login_user
from utils.rest import update,\
                       expect_json_data,\
                       login_or_api_key_required
import gspread
from oauth2client.service_account import ServiceAccountCredentials


from models.api_errors import ApiErrors
from utils.includes import USERS_INCLUDES

def make_user_query():
    query = app.model.User.query
    return query

@app.route("/users/me", methods=["GET"])
@login_required
def get_profile():
    user = current_user._asdict(include=USERS_INCLUDES)
    return jsonify(user)

@app.route('/users/me', methods=['PATCH'])
@login_or_api_key_required
@expect_json_data
def patch_profile():
    update(current_user, request.json)
    app.model.PcObject.check_and_save(current_user)
    return jsonify(current_user._asdict(include=USERS_INCLUDES)), 200


@app.route("/users/signin", methods=["POST"])
def signin():
    json = request.get_json()
    identifier = json.get("identifier")
    password = json.get("password")
    user = app.get_user_with_credentials(identifier, password)
    return jsonify(user._asdict(include=USERS_INCLUDES)), 200


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

    departement_code = None
    if 'email' in request.json:
        scope = ['https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive']
        key_path = Path(path.dirname(path.realpath(__file__))) / '..' / 'private' / 'google_key.json'
        credentials = ServiceAccountCredentials.from_json_keyfile_name(key_path, scope)

        gc = gspread.authorize(credentials)

        spreadsheet = gc.open_by_key('1YCLVZNU5Gzb2P4Jaf9OW50Oedm2-Z9S099FGitFG64s')
        worksheet = spreadsheet.worksheet('Utilisateurs')

        labels = worksheet.row_values(1)
        email_index = None
        departement_index = None
        for index, label in enumerate(labels):
            if label == 'Email':
                email_index = index
            elif label == 'Département':
                departement_index = index
        if email_index is None:
            raise ValueError("Can't find 'Email' column in users spreadsheet")
        if departement_index is None:
            raise ValueError("Can't find 'Département' column in users spreadsheet")

        values = worksheet.get_all_values()[1:]

        authorized_emails = list(map(lambda v: v[email_index],
                                     values))

        try:
            email_index = authorized_emails.index(request.json['email'])
        except ValueError:
            e = ApiErrors()
            e.addError('email', "Addresse non autorisée pour l'expérimentation")
            return jsonify(e.errors), 400

        departement_code = values[email_index][departement_index]
        if departement_code.strip() == '':
            print("[ERROR] Missing departement code in users spreadsheet for "
                  + request.json['email'])

            e = ApiErrors()
            e.addError('email', "Addresse non autorisée pour l'expérimentation")
            return jsonify(e.errors), 400


    new_user = app.model.User(from_dict=request.json)
    new_user.id = None
    new_user.departementCode = departement_code

    offerer = None
    user_offerer = None
    if 'siren' in request.json:
        #TODO: handle case of already existing Offerer
        offerer = app.model.Offerer()
        update(offerer, request.json)
        user_offerer = offerer.make_admin(new_user)
        offerer.bookingEmail = new_user.email
        offerer.isActive = False
        app.model.PcObject.check_and_save(new_user, offerer, user_offerer)
    else:
        app.model.PcObject.check_and_save(new_user)

    login_user(new_user)
    return jsonify(new_user._asdict(include=USERS_INCLUDES)), 201
