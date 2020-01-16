from flask import current_app as app, request
from flask_login import current_user, login_required

from domain.password import validate_reset_request, check_reset_token_validity, validate_new_password_request, \
    check_password_strength, check_new_password_validity, generate_reset_token, validate_change_password_request
from domain.user_emails import send_reset_password_email_with_mailjet_template, send_reset_password_email
from models import ApiErrors
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
    new_password = request.get_json()['newPassword']
    old_password = json.get('oldPassword')
    check_password_strength('newPassword', new_password)
    check_new_password_validity(current_user, old_password, new_password)
    current_user.setPassword(new_password)
    Repository.save(current_user)
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
    Repository.save(user)
    app_origin_url = request.headers.get('origin')

    try:
        if user.canBookFreeOffers:
            send_reset_password_email_with_mailjet_template(user, send_raw_email)
        else:
            send_reset_password_email(user, send_raw_email, app_origin_url)

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
        errors.add_error('token', 'Votre lien de changement de mot de passe est invalide.')
        raise errors

    check_reset_token_validity(user)
    check_password_strength('newPassword', new_password)
    user.setPassword(new_password)
    Repository.save(user)

    return '', 204
