""" validate """

from flask import current_app as app, jsonify, request
from flask_login import login_required, current_user

from connectors import redis
from domain.admin_emails import maybe_send_offerer_validation_email
from domain.iris import link_valid_venue_to_irises
from domain.payments import read_message_name_in_message_file, \
    generate_file_checksum
from domain.user_emails import send_validation_confirmation_email_to_pro, \
    send_venue_validation_confirmation_email, \
    send_attachment_validation_email_to_pro_offerer, \
    send_pro_user_waiting_for_validation_by_admin_email, send_ongoing_offerer_attachment_information_email_to_pro
from models import ApiErrors, \
    UserOfferer, Offerer, Venue
from models.api_errors import ResourceNotFoundError, ForbiddenError
from models.feature import FeatureToggle
from repository import user_offerer_queries, user_queries, repository, feature_queries
from repository.payment_queries import find_message_checksum
from repository.user_offerer_queries import count_pro_attached_to_offerer
from utils.config import IS_INTEGRATION
from utils.mailing import MailServiceException, send_raw_email
from validation.routes.users import check_validation_token_has_been_already_used
from validation.routes.validate import check_valid_token_for_user_validation, check_validation_request, check_venue_found


@app.route("/validate/user-offerer/<token>", methods=["GET"])
def validate_offerer_attachment(token):
    check_validation_request(token)
    user_offerer = UserOfferer.query.filter_by(validationToken=token).first()
    check_validation_token_has_been_already_used(user_offerer)

    user_offerer.validationToken = None
    repository.save(user_offerer)

    try:
        send_attachment_validation_email_to_pro_offerer(user_offerer, send_raw_email)
    except MailServiceException as e:
        app.logger.error('Mail service failure', e)

    return "Validation du rattachement de la structure effectuée", 202


@app.route("/validate/offerer/<token>", methods=["GET"])
def validate_new_offerer(token):
    check_validation_request(token)
    offerer = Offerer.query.filter_by(validationToken=token).first()
    check_validation_token_has_been_already_used(offerer)

    offerer.validationToken = None

    for venue in offerer.managedVenues:
        link_valid_venue_to_irises(venue)

    repository.save(offerer)

    try:
        send_validation_confirmation_email_to_pro(offerer, send_raw_email)
    except MailServiceException as e:
        app.logger.error('Mail service failure', e)
    return "Validation effectuée", 202


@app.route("/validate/venue/", methods=["GET"])
def validate_venue():
    token = request.args.get('token')
    check_validation_request(token)
    venue = Venue.query.filter_by(validationToken=token).first()
    check_venue_found(venue)
    venue.validationToken = None
    link_valid_venue_to_irises(venue)
    repository.save(venue)
    if feature_queries.is_active(FeatureToggle.SYNCHRONIZE_ALGOLIA):
        redis.add_venue_id(client=app.redis_client, venue_id=venue.id)

    try:
        send_venue_validation_confirmation_email(venue, send_raw_email)
    except MailServiceException as e:
        app.logger.error('Mail service failure', e)

    return "Validation effectuée", 202


@app.route("/validate/user/<token>", methods=["PATCH"])
def validate_user(token):
    user_to_validate = user_queries.find_by_validation_token(token)
    check_valid_token_for_user_validation(user_to_validate)

    user_to_validate.validationToken = None
    repository.save(user_to_validate)

    user_offerer = user_offerer_queries.find_one_or_none_by_user_id(user_to_validate.id)

    if user_offerer:
        number_of_pro_attached_to_offerer = count_pro_attached_to_offerer(user_offerer.offererId)
        offerer = user_offerer.offerer

        if IS_INTEGRATION:
            _validate_offerer(offerer, user_offerer)
        else:
            _ask_for_validation(offerer, user_offerer)

        if number_of_pro_attached_to_offerer > 1:
            try:
                send_ongoing_offerer_attachment_information_email_to_pro(user_offerer, send_raw_email)
            except MailServiceException as mail_service_exception:
                app.logger.error('[send_ongoing_offerer_attachment_information_email_to_pro] '
                                 'Mail service failure', mail_service_exception)
        else:
            try:
                send_pro_user_waiting_for_validation_by_admin_email(user_to_validate, send_raw_email, offerer)
            except MailServiceException as mail_service_exception:
                app.logger.error('[send_pro_user_waiting_for_validation_by_admin_email] '
                                 'Mail service failure', mail_service_exception)

    return '', 204


@app.route('/validate/payment_message', methods=['POST'])
@login_required
def certify_message_file_authenticity():
    if not current_user.isAdmin:
        raise ForbiddenError()

    xml_content = request.files['file'].read().decode('utf-8')
    message_id = read_message_name_in_message_file(xml_content)
    found_checksum = find_message_checksum(message_id)

    if not found_checksum:
        raise ResourceNotFoundError({'xml': ["L'identifiant du document XML 'MsgId' est inconnu"]})

    given_checksum = generate_file_checksum(xml_content)

    if found_checksum != given_checksum:
        raise ApiErrors({'xml': [
            "L'intégrité du document n'est pas validée car la somme de contrôle est invalide : %s" % given_checksum.hex()]})

    return jsonify({'checksum': given_checksum.hex()}), 200


def _ask_for_validation(offerer: Offerer, user_offerer: UserOfferer):
    try:
        maybe_send_offerer_validation_email(offerer, user_offerer, send_raw_email)

    except MailServiceException as e:
        app.logger.error('Mail service failure', e)


def _validate_offerer(offerer: Offerer, user_offerer: UserOfferer):
    offerer.validationToken = None
    user_offerer.validationToken = None
    repository.save(offerer, user_offerer)
