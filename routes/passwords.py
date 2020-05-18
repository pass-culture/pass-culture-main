from flask import current_app as app, request
from flask_login import current_user, login_required

from domain.password import validate_reset_request, check_reset_token_validity, validate_new_password_request, \
    check_password_strength, generate_reset_token, validate_change_password_request, \
    check_password_validity
from domain.user_emails import send_reset_password_email_to_user, \
    send_reset_password_email_to_pro
from models import ApiErrors
from repository import repository
from repository.user_queries import find_user_by_email, find_user_by_reset_password_token
from utils.mailing import \
    MailServiceException, send_raw_email
from utils.rest import expect_json_data


@app.route('/users/current/change-password', methods=['POST'])
@login_required
@expect_json_data
def post_change_password():
    json = request.get_json()
    validate_change_password_request(json)
    user = find_user_by_email(current_user.email)
    new_password = json['newPassword']
    old_password = json.get('oldPassword')
    check_password_validity(new_password, old_password, user)
    user.setPassword(new_password)
    repository.save(user)
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
    repository.save(user)

    is_not_pro_user = user.canBookFreeOffers

    if is_not_pro_user:
        try:
            send_reset_password_email_to_user(user, send_raw_email)
        except MailServiceException as mail_service_exception:
            app.logger.error('[send_reset_password_email_to_user] '
                             'Mail service failure', mail_service_exception)
    else:
        try:
            send_reset_password_email_to_pro(user, send_raw_email)
        except MailServiceException as mail_service_exception:
            app.logger.error('[send_reset_password_email_to_pro] '
                             'Mail service failure', mail_service_exception)

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
        errors.add_error('token', 'Votre lien de changement de mot de passe est invalide.')
        raise errors

    check_reset_token_validity(user)
    check_password_strength('newPassword', new_password)

    user.setPassword(new_password)
    repository.save(user)

    return '', 204
