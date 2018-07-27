"""users routes"""
from os import path
import os, json
from pathlib import Path
import gspread
from flask import current_app as app, jsonify, request
from flask_login import current_user, login_required, logout_user, login_user
from oauth2client.service_account import ServiceAccountCredentials
from sqlalchemy.exc import IntegrityError

from utils.config import ILE_DE_FRANCE_DEPT_CODES
from models.api_errors import ApiErrors
from models.offerer import Offerer
from models.pc_object import PcObject
from models.user import User
from models.user_offerer import RightsType
from utils.credentials import get_user_with_credentials
from utils.includes import USER_INCLUDES
from utils.mailing import maybe_send_offerer_validation_email, \
    subscribe_newsletter
from utils.rest import expect_json_data, \
    login_or_api_key_required


def make_user_query():
    query = User.query
    return query


def is_pro_signup(json_user):
    return 'siren' in json_user


@app.route("/users/current", methods=["GET"])
@login_required
def get_profile():
    user = current_user._asdict(include=USER_INCLUDES)
    return jsonify(user)


@app.route('/users/current', methods=['PATCH'])
@login_or_api_key_required
@expect_json_data
def patch_profile():
    current_user.populateFromDict(request.json)
    PcObject.check_and_save(current_user)
    return jsonify(current_user._asdict(include=USER_INCLUDES)), 200


@app.route("/users/signin", methods=["POST"])
def signin():
    json = request.get_json()
    identifier = json.get("identifier")
    password = json.get("password")
    user = get_user_with_credentials(identifier, password)
    return jsonify(user._asdict(include=USER_INCLUDES)), 200


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
        raise e

    departement_code = None
    if 'email' in request.json and not is_pro_signup(request.json):
        scope = ['https://spreadsheets.google.com/feeds',
                 'https://www.googleapis.com/auth/drive']

        if "PC_GOOGLE_KEY" in os.environ:
            google_key_json_payload = json.loads(os.environ.get("PC_GOOGLE_KEY"))
            key_path = '/tmp/data.json'
            with open(key_path, 'w') as outfile:
                json.dump(google_key_json_payload, outfile)
            credentials = ServiceAccountCredentials.from_json_keyfile_name(key_path, scope)
            os.remove(key_path)
        else:
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
            e.addError('email', "Adresse non autorisée pour l'expérimentation")
            raise e

        departement_code = values[email_index][departement_index]
        if departement_code.strip() == '':
            print("[ERROR] Missing departement code in users spreadsheet for "
                  + request.json['email'])

            e = ApiErrors()
            e.addError('email', "Adresse non autorisée pour l'expérimentation")
            raise e

    new_user = User(from_dict=request.json)
    new_user.id = None
    new_user.departementCode = departement_code

    offerer = None
    user_offerer = None
    # we don't validate users yet
    # new_user.generate_validation_token()
    if is_pro_signup(request.json):
        new_user.canBook = False
        existing_offerer = Offerer.query.filter_by(siren=request.json['siren']).first()
        if existing_offerer is None:
            offerer = Offerer()
            offerer.populateFromDict(request.json)
            offerer.generate_validation_token()
            if offerer.postalCode is not None:
                offerer_dept_code = offerer.postalCode[:2]
                new_user.departementCode = '93' if offerer_dept_code in ILE_DE_FRANCE_DEPT_CODES\
                                                else offerer_dept_code
            else:
                new_user.departementCode = 'XX' # We don't want to trigger an error on this:
                                                # we want the error on user
            user_offerer = offerer.give_rights(new_user,
                                               RightsType.admin)
            # offerer.bookingEmail = new_user.email
            # Don't validate the first user / offerer link so that the user can immediately start loading offers
            objects_to_save = [new_user, offerer, user_offerer]
        else:
            offerer = existing_offerer
            new_user.departementCode = offerer.postalCode[:2]
            user_offerer = offerer.give_rights(new_user,
                                               RightsType.editor)
            user_offerer.generate_validation_token()
            objects_to_save = [new_user]
        maybe_send_offerer_validation_email(new_user, offerer, user_offerer)
    else:
        objects_to_save = [new_user]
    try:
        PcObject.check_and_save(*objects_to_save)
    except IntegrityError as ie:
        e = ApiErrors()
        if "check_admin_cannot_book" in str(ie.orig):
            e.addError('canBook', 'Admin ne peut pas booker')
        raise e



    if request.json.get('contact_ok'):
        subscribe_newsletter(new_user)
    login_user(new_user)
    return jsonify(new_user._asdict(include=USER_INCLUDES)), 201
