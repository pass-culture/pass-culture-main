"""users routes"""

from flask import current_app as app, jsonify, request
from flask_login import current_user, login_required, logout_user, login_user

from connectors.google_spreadsheet import get_authorized_emails_and_dept_codes
from domain.admin_emails import maybe_send_offerer_validation_email
from domain.expenses import get_expenses
from domain.password import validate_reset_request, check_reset_token_validity, validate_new_password_request, \
    check_password_strength, check_new_password_validity, generate_reset_token, validate_change_password_request
from domain.user_emails import send_reset_password_email, send_user_validation_email
from models import ApiErrors, Deposit, Offerer, PcObject, User
from models.user_offerer import RightsType
from models.venue import create_digital_venue
from repository.user_queries import find_user_by_email, find_user_by_reset_password_token
from utils import logger
from utils.config import ILE_DE_FRANCE_DEPT_CODES, IS_INTEGRATION
from utils.credentials import get_user_with_credentials
from utils.includes import USER_INCLUDES
from utils.login_manager import stamp_session, discard_session
from utils.mailing import \
    subscribe_newsletter, MailServiceException
from utils.rest import expect_json_data, \
    login_or_api_key_required
from validation.users import check_allowed_changes_for_user, check_valid_signup


def is_pro_signup(json_user):
    return 'siren' in json_user


@app.route("/users/current", methods=["GET"])
@login_required
def get_profile():
    user = current_user._asdict(include=USER_INCLUDES)
    user['expenses'] = get_expenses(current_user.userBookings)
    return jsonify(user)


@app.route('/users/current', methods=['PATCH'])
@login_or_api_key_required
@expect_json_data
def patch_profile():
    data = request.json.keys()
    check_allowed_changes_for_user(data)
    current_user.populateFromDict(request.json)
    PcObject.check_and_save(current_user)
    user = current_user._asdict(include=USER_INCLUDES)
    user['expenses'] = get_expenses(current_user.userBookings)
    return jsonify(user), 200


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
    login_user(user, remember=True)
    stamp_session(user)
    user_dict = user._asdict(include=USER_INCLUDES)
    user_dict['expenses'] = get_expenses(user.userBookings)
    return jsonify(user_dict), 200


@app.route("/users/signout", methods=["GET"])
@login_required
def signout():
    discard_session()
    logout_user()
    return jsonify({"global": "Deconnecté"})


@app.route("/users/signup", methods=["POST"])
def signup():
    objects_to_save = []
    email = request.json.get('email')
    password = request.json.get('password')
    check_valid_signup(request)
    check_password_strength('password', password)
    do_pro_signup = is_pro_signup(request.json)
    need_for_authorisation_check = email is not None and not do_pro_signup and not IS_INTEGRATION

    new_user = User(from_dict=request.json)
    if need_for_authorisation_check:
        authorized_emails, department_codes = get_authorized_emails_and_dept_codes()
        departement_code = _get_departement_code_when_authorized_or_error(authorized_emails, department_codes)
        new_user.departementCode = departement_code

    if do_pro_signup:
        existing_offerer = Offerer.query.filter_by(siren=request.json['siren']).first()
        if existing_offerer is None:
            offerer = _generate_offerer(request.json)
            user_offerer = offerer.give_rights(new_user, RightsType.editor)
            # Don't validate the first user / offerer link so that the user can immediately start loading stocks
            digital_venue = create_digital_venue(offerer)
            objects_to_save.extend([digital_venue, offerer])
        else:
            user_offerer = _generate_user_offerer_when_existing_offerer(new_user, existing_offerer)
            offerer = existing_offerer
        objects_to_save.append(user_offerer)
        new_user.canBookFreeOffers = False
        new_user = _set_offerer_departement_code(new_user, offerer)
    else:
        if IS_INTEGRATION:
            new_user.departementCode = '00'
            objects_to_save.append(_create_initial_deposit(new_user))

    objects_to_save.append(new_user)

    PcObject.check_and_save(*objects_to_save)

    if do_pro_signup:
        try:
            maybe_send_offerer_validation_email(offerer, user_offerer, app.mailjet_client.send.create)
        except MailServiceException as e:
            app.logger.error('Mail service failure', e)

    if request.json.get('contact_ok'):
        subscribe_newsletter(new_user)

    login_user(new_user)
    stamp_session(new_user)

    return jsonify(new_user._asdict(include=USER_INCLUDES)), 201


@app.route("/users/signup/webapp", methods=["POST"])
def signup_webapp():
    objects_to_save = []
    password = request.json.get('password')
    app_origin_url = request.headers.get('origin')
    check_valid_signup(request)
    check_password_strength('password', password)

    new_user = User(from_dict=request.json)

    if IS_INTEGRATION:
        new_user.departementCode = '00'
        objects_to_save.append(_create_initial_deposit(new_user))
    else:
        authorized_emails, department_codes = get_authorized_emails_and_dept_codes()
        departement_code = _get_departement_code_when_authorized_or_error(authorized_emails, department_codes)
        new_user.departementCode = departement_code

    new_user.generate_validation_token()
    objects_to_save.append(new_user)

    PcObject.check_and_save(*objects_to_save)
    try:
        send_user_validation_email(new_user, app.mailjet_client.send.create, app_origin_url, is_webapp=True)
    except MailServiceException as e:
        app.logger.error('Mail service failure', e)

    if request.json.get('contact_ok'):
        subscribe_newsletter(new_user)

    return jsonify(new_user._asdict(include=USER_INCLUDES)), 201


@app.route("/users/signup/pro", methods=["POST"])
def signup_pro():
    objects_to_save = []
    password = request.json.get('password')
    app_origin_url = request.headers.get('origin')

    check_valid_signup(request)
    check_password_strength('password', password)
    new_user = User(from_dict=request.json)

    existing_offerer = Offerer.query.filter_by(siren=request.json['siren']).first()
    if existing_offerer:
        user_offerer = _generate_user_offerer_when_existing_offerer(new_user, existing_offerer)
        offerer = existing_offerer
    else:
        offerer = _generate_offerer(request.json)
        user_offerer = offerer.give_rights(new_user, RightsType.editor)
        digital_venue = create_digital_venue(offerer)
        objects_to_save.extend([digital_venue, offerer])
    objects_to_save.append(user_offerer)
    new_user.canBookFreeOffers = False
    new_user = _set_offerer_departement_code(new_user, offerer)

    new_user.generate_validation_token()
    objects_to_save.append(new_user)

    PcObject.check_and_save(*objects_to_save)

    try:
        send_user_validation_email(new_user, app.mailjet_client.send.create, app_origin_url, is_webapp=False)
        subscribe_newsletter(new_user)
    except MailServiceException as e:
        app.logger.error('Mail service failure', e)

    return jsonify(new_user._asdict(include=USER_INCLUDES)), 201


def _generate_user_offerer_when_existing_offerer(new_user, offerer):
    user_offerer = offerer.give_rights(new_user, RightsType.editor)
    if not IS_INTEGRATION:
        user_offerer.generate_validation_token()
    return user_offerer


def _create_initial_deposit(new_user):
    deposit = Deposit()
    deposit.amount = 499.99
    deposit.user = new_user
    deposit.source = 'test'
    return deposit


def _generate_offerer(data):
    offerer = Offerer()
    offerer.populateFromDict(data)
    if not IS_INTEGRATION:
        offerer.generate_validation_token()
    return offerer


def _set_offerer_departement_code(new_user, offerer):
    if IS_INTEGRATION:
        new_user.departementCode = '00'
    elif offerer.postalCode is not None:
        offerer_dept_code = offerer.postalCode[:2]
        new_user.departementCode = '93' if offerer_dept_code in ILE_DE_FRANCE_DEPT_CODES \
            else offerer_dept_code
    else:
        new_user.departementCode = 'XX'  # We don't want to trigger an error on this:
        # we want the error on user
    return new_user


def _get_departement_code_when_authorized_or_error(authorized_emails, department_codes):
    email_index = _get_email_index_in_spreadsheet_or_error(authorized_emails)
    departement_code = department_codes[email_index]
    if departement_code.strip() == '':
        logger.error("[ERROR] Missing departement code in users spreadsheet for "
                     + request.json['email'])

        e = ApiErrors()
        e.addError('email', "Adresse non autorisée pour l'expérimentation")
        raise e
    return departement_code


def _get_email_index_in_spreadsheet_or_error(authorized_emails):
    try:
        email_index = authorized_emails.index(request.json['email'])
    except ValueError:
        e = ApiErrors()
        e.addError('email', "Adresse non autorisée pour l'expérimentation")
        raise e
    return email_index
