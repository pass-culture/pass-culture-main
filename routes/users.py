"""users routes"""

from flask import current_app as app, jsonify, request
from flask_login import current_user, login_required, logout_user, login_user

from connectors.google_spreadsheet import get_authorized_emails_and_dept_codes
from domain.booking_emails import send_reset_password_email
from domain.expenses import get_expenses
from domain.admin_emails import maybe_send_offerer_validation_email
from domain.password import validate_reset_request, check_reset_token_validity, validate_new_password_request, \
    check_password_strength, check_new_password_validity, generate_reset_token, validate_change_password_request
from models import ApiErrors, Offerer, PcObject, User
from models.user_offerer import RightsType
from models.venue import create_digital_venue
from repository.user_queries import find_user_by_email, find_user_by_reset_password_token
from utils.config import ILE_DE_FRANCE_DEPT_CODES
from utils.credentials import get_user_with_credentials
from utils.includes import USER_INCLUDES
from utils.mailing import \
    subscribe_newsletter, MailServiceException
from utils.rest import expect_json_data, \
    login_or_api_key_required


def is_pro_signup(json_user):
    return 'siren' in json_user


@app.route("/users/current", methods=["GET"])
@login_required
def get_profile():
    user = current_user._asdict(include=USER_INCLUDES)
    user['expenses'] = get_expenses(current_user)
    return jsonify(user)


@app.route('/users/current', methods=['PATCH'])
@login_or_api_key_required
@expect_json_data
def patch_profile():
    current_user.populateFromDict(request.json)
    PcObject.check_and_save(current_user)
    return jsonify(current_user._asdict(include=USER_INCLUDES)), 200


@app.route('/users/current/change-password', methods=['POST'])
@login_required
@expect_json_data
def post_change_password():
    json = request.get_json()
    validate_change_password_request(json)
    new_password = request.get_json()['newPassword']
    old_password = json.get('oldPassword')
    check_password_strength('newPassword', new_password)
    check_new_password_validity(current_user, old_password, new_password)
    current_user.setPassword(new_password)
    PcObject.check_and_save(current_user)
    return '', 204


@app.route("/users/reset-password", methods=['POST'])
@expect_json_data
def post_for_password_token():
    validate_reset_request(request)
    email = request.get_json()['email']
    user = find_user_by_email(email)

    if not user:
        return '', 204

    generate_reset_token(user)
    PcObject.check_and_save(user)
    app_origin_url = request.headers.get('origin')

    try:
        send_reset_password_email(user, app.mailjet_client.send.create, app_origin_url)
    except MailServiceException as e:
        app.logger.error('Mail service failure', e)

    return '', 204


@app.route("/users/new-password", methods=['POST'])
@expect_json_data
def post_new_password():
    validate_new_password_request(request)
    token = request.get_json()['token']
    new_password = request.get_json()['newPassword']
    user = find_user_by_reset_password_token(token)

    if not user:
        errors = ApiErrors()
        errors.addError('token', 'Votre lien de changement de mot de passe est invalide.')
        raise errors

    check_reset_token_validity(user)
    check_password_strength('newPassword', new_password)
    user.setPassword(new_password)
    PcObject.check_and_save(user)
    return '', 204


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
    missing_field_contact_ok = 'contact_ok' not in request.json
    if missing_field_contact_ok or _contact_ok_is_not_checked(request.json):
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
    do_pro_signup = is_pro_signup(request.json)
    if do_pro_signup:
        new_user.canBookFreeOffers = False
        existing_offerer = Offerer.query.filter_by(siren=request.json['siren']).first()
        if existing_offerer is None:
            offerer = Offerer()
            offerer.populateFromDict(request.json)
            offerer.generate_validation_token()
            if offerer.postalCode is not None:
                offerer_dept_code = offerer.postalCode[:2]
                new_user.departementCode = '93' if offerer_dept_code in ILE_DE_FRANCE_DEPT_CODES \
                    else offerer_dept_code
            else:
                new_user.departementCode = 'XX'  # We don't want to trigger an error on this:
                # we want the error on user
            user_offerer = offerer.give_rights(new_user,
                                               RightsType.admin)
            # offerer.bookingEmail = new_user.email
            # Don't validate the first user / offerer link so that the user can immediately start loading stocks
            digital_venue = create_digital_venue(offerer)
            objects_to_save = [digital_venue, new_user, offerer, user_offerer]
        else:
            offerer = existing_offerer
            new_user.departementCode = offerer.postalCode[:2]
            user_offerer = offerer.give_rights(new_user,
                                               RightsType.editor)
            user_offerer.generate_validation_token()
            objects_to_save = [new_user, user_offerer]
    else:
        objects_to_save = [new_user]

    PcObject.check_and_save(*objects_to_save)

    if do_pro_signup:
        maybe_send_offerer_validation_email(offerer, user_offerer, app.mailjet_client.send.create)

    if request.json.get('contact_ok'):
        subscribe_newsletter(new_user)

    login_user(new_user)

    return jsonify(new_user._asdict(include=USER_INCLUDES)), 201


def _contact_ok_is_not_checked(request_json):
    contact_ok_is_not_checked_as_bool = request_json['contact_ok'] is not True
    contact_ok_is_not_checked_as_str = str(request_json['contact_ok']).lower() != 'true'
    return contact_ok_is_not_checked_as_bool and contact_ok_is_not_checked_as_str
