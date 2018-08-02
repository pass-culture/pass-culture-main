"""users routes"""
from flask import current_app as app, jsonify, request
from flask_login import current_user, login_required, logout_user, login_user
from sqlalchemy.exc import IntegrityError

from connectors.google_spreadsheet import get_authorized_emails_and_dept_codes
from models.api_errors import ApiErrors
from models.offerer import Offerer
from models.pc_object import PcObject
from models.user import User
from models.user_offerer import RightsType
from utils.config import ILE_DE_FRANCE_DEPT_CODES
from utils.credentials import get_user_with_credentials
from utils.includes import USER_INCLUDES
from utils.mailing import maybe_send_offerer_validation_email, \
    subscribe_newsletter
from utils.rest import expect_json_data, \
    login_or_api_key_required


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


@app.route("/users/signup", methods=["POST"])
def signup():
    if 'contact_ok' not in request.json or\
       (request.json['contact_ok'] is not True and
        str(request.json['contact_ok']).lower() != 'true'):
        e = ApiErrors()
        e.addError('contact_ok', 'Vous devez obligatoirement cocher cette case')
        raise e

    departement_code = None
    if 'email' in request.json and not is_pro_signup(request.json):

        authorized_emails, departement_codes = get_authorized_emails_and_dept_codes()
        try:
            email_index = authorized_emails.index(request.json['email'])
        except ValueError:
            e = ApiErrors()
            e.addError('email', "Adresse non autorisée pour l'expérimentation")
            raise e

        departement_code = departement_codes[email_index]
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
        new_user.canBookFreeOffers = False
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
            # Don't validate the first user / offerer link so that the user can immediately start loading stocks
            objects_to_save = [new_user, offerer, user_offerer]
        else:
            offerer = existing_offerer
            new_user.departementCode = offerer.postalCode[:2]
            user_offerer = offerer.give_rights(new_user,
                                               RightsType.editor)
            user_offerer.generate_validation_token()
            objects_to_save = [user_offerer]
        maybe_send_offerer_validation_email(new_user, offerer, user_offerer)
    else:
        objects_to_save = [new_user]
    try:

        PcObject.check_and_save(*objects_to_save)
    except IntegrityError as ie:
        e = ApiErrors()
        if "check_admin_cannot_book_free_offers" in str(ie.orig):
            e.addError('canBookFreeOffers', 'Admin ne peut pas booker')
        raise e

    if request.json.get('contact_ok'):
        subscribe_newsletter(new_user)
    login_user(new_user)
    return jsonify(new_user._asdict(include=USER_INCLUDES)), 201
