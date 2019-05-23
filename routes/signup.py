from flask import current_app as app, jsonify, request, redirect

from connectors.google_spreadsheet import get_authorized_emails_and_dept_codes
from domain.departments import ILE_DE_FRANCE_DEPT_CODES
from domain.password import check_password_strength
from domain.user_emails import send_user_validation_email
from models import ApiErrors, Deposit, Offerer, PcObject, User
from models.user_offerer import RightsType
from models.venue import create_digital_venue
from utils.config import IS_INTEGRATION
from utils.includes import USER_INCLUDES
from utils.logger import logger
from utils.mailing import \
    subscribe_newsletter, MailServiceException, send_raw_email
from validation.users import check_valid_signup


@app.route("/users/signup", methods=["POST"])
def signup_old():
    return redirect("/users/signup/webapp", code=308)


@app.route("/users/signup/webapp", methods=["POST"])
def signup_webapp():
    objects_to_save = []
    password = request.json.get('password')
    check_valid_signup(request)
    check_password_strength('password', password)

    new_user = User(from_dict=request.json)

    if IS_INTEGRATION:
        new_user.departementCode = '00'
        objects_to_save.append(_create_initial_deposit(new_user))
    else:
        authorized_emails, departement_codes = get_authorized_emails_and_dept_codes()
        departement_code = _get_departement_code_when_authorized_or_error(authorized_emails, departement_codes)
        new_user.departementCode = departement_code

    new_user.canBookFreeOffers = False
    new_user.isAdmin = False
    objects_to_save.append(new_user)

    PcObject.check_and_save(*objects_to_save)

    if request.json.get('contact_ok'):
        subscribe_newsletter(new_user)

    return jsonify(new_user.as_dict(include=USER_INCLUDES)), 201


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
    new_user.isAdmin = False
    new_user = _set_offerer_departement_code(new_user, offerer)

    new_user.generate_validation_token()
    objects_to_save.append(new_user)

    PcObject.check_and_save(*objects_to_save)

    try:
        send_user_validation_email(new_user, send_raw_email, app_origin_url, is_webapp=False)
        subscribe_newsletter(new_user)
    except MailServiceException as e:
        app.logger.error('Mail service failure', e)

    return jsonify(new_user.as_dict(include=USER_INCLUDES)), 201


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


def _get_departement_code_when_authorized_or_error(authorized_emails, departement_codes):
    email_index = _get_email_index_in_spreadsheet_or_error(authorized_emails)
    departement_code = departement_codes[email_index]
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


def _is_pro_signup(json_user):
    return 'siren' in json_user
