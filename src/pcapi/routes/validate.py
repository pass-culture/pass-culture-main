from flask import current_app as app
from flask import jsonify
from flask import request
from flask_login import current_user
from flask_login import login_required

from pcapi.connectors import redis
from pcapi.domain.admin_emails import maybe_send_offerer_validation_email
from pcapi.domain.iris import link_valid_venue_to_irises
from pcapi.domain.payments import generate_file_checksum
from pcapi.domain.payments import read_message_name_in_message_file
from pcapi.domain.user_emails import send_attachment_validation_email_to_pro_offerer
from pcapi.domain.user_emails import send_ongoing_offerer_attachment_information_email_to_pro
from pcapi.domain.user_emails import send_pro_user_waiting_for_validation_by_admin_email
from pcapi.domain.user_emails import send_validation_confirmation_email_to_pro
from pcapi.domain.user_emails import send_venue_validation_confirmation_email
from pcapi.flask_app import private_api
from pcapi.flask_app import public_api
from pcapi.models import ApiErrors
from pcapi.models import Offerer
from pcapi.models import UserOfferer
from pcapi.models import VenueSQLEntity
from pcapi.models.api_errors import ForbiddenError
from pcapi.models.api_errors import ResourceNotFoundError
from pcapi.models.feature import FeatureToggle
from pcapi.repository import feature_queries
from pcapi.repository import repository
from pcapi.repository import user_offerer_queries
from pcapi.repository import user_queries
from pcapi.repository.payment_queries import find_message_checksum
from pcapi.repository.user_offerer_queries import count_pro_attached_to_offerer
from pcapi.utils.config import IS_INTEGRATION
from pcapi.utils.mailing import MailServiceException
from pcapi.utils.mailing import send_raw_email
from pcapi.validation.routes.users import check_validation_token_has_been_already_used
from pcapi.validation.routes.validate import check_valid_token_for_user_validation
from pcapi.validation.routes.validate import check_validation_request
from pcapi.validation.routes.validate import check_venue_found


@public_api.route("/validate/user-offerer/<token>", methods=["GET"])
def validate_offerer_attachment(token):
    check_validation_request(token)
    user_offerer = UserOfferer.query.filter_by(validationToken=token).first()
    check_validation_token_has_been_already_used(user_offerer)

    user_offerer.validationToken = None
    repository.save(user_offerer)

    try:
        send_attachment_validation_email_to_pro_offerer(user_offerer, send_raw_email)
    except MailServiceException as mail_service_exception:
        app.logger.exception("Email service failure", mail_service_exception)

    return "Validation du rattachement de la structure effectuée", 202


@public_api.route("/validate/offerer/<token>", methods=["GET"])
def validate_new_offerer(token):
    check_validation_request(token)
    offerer = Offerer.query.filter_by(validationToken=token).first()
    check_validation_token_has_been_already_used(offerer)
    offerer.validationToken = None
    managed_venues = offerer.managedVenues

    for venue in managed_venues:
        link_valid_venue_to_irises(venue)

    repository.save(offerer)
    if feature_queries.is_active(FeatureToggle.SYNCHRONIZE_ALGOLIA):
        venue_ids = map(lambda managed_venue: managed_venue.id, managed_venues)
        sorted_venue_ids = sorted(venue_ids, key=int)
        for venue_id in sorted_venue_ids:
            redis.add_venue_id(client=app.redis_client, venue_id=venue_id)

    try:
        send_validation_confirmation_email_to_pro(offerer, send_raw_email)
    except MailServiceException as mail_service_exception:
        app.logger.exception("Email service failure", mail_service_exception)
    return "Validation effectuée", 202


@public_api.route("/validate/venue/", methods=["GET"])
def validate_venue():
    token = request.args.get("token")
    check_validation_request(token)
    venue = VenueSQLEntity.query.filter_by(validationToken=token).first()
    check_venue_found(venue)
    venue.validationToken = None
    link_valid_venue_to_irises(venue)
    repository.save(venue)
    if feature_queries.is_active(FeatureToggle.SYNCHRONIZE_ALGOLIA):
        redis.add_venue_id(client=app.redis_client, venue_id=venue.id)

    try:
        send_venue_validation_confirmation_email(venue, send_raw_email)
    except MailServiceException as mail_service_exception:
        app.logger.exception("Email service failure", mail_service_exception)

    return "Validation effectuée", 202


@private_api.route("/validate/user/<token>", methods=["PATCH"])
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
                app.logger.exception(
                    "[send_ongoing_offerer_attachment_information_email_to_pro] " "Email service failure",
                    mail_service_exception,
                )
        else:
            try:
                send_pro_user_waiting_for_validation_by_admin_email(user_to_validate, send_raw_email, offerer)
            except MailServiceException as mail_service_exception:
                app.logger.exception(
                    "[send_pro_user_waiting_for_validation_by_admin_email] " "Email service failure",
                    mail_service_exception,
                )

    return "", 204


@private_api.route("/validate/payment_message", methods=["POST"])
@login_required
def certify_message_file_authenticity():
    if not current_user.isAdmin:
        raise ForbiddenError()

    xml_content = request.files["file"].read().decode("utf-8")
    message_id = read_message_name_in_message_file(xml_content)
    found_checksum = find_message_checksum(message_id)

    if not found_checksum:
        raise ResourceNotFoundError({"xml": ["L'identifiant du document XML 'MsgId' est inconnu"]})

    given_checksum = generate_file_checksum(xml_content)

    if found_checksum != given_checksum:
        raise ApiErrors(
            {
                "xml": [
                    "L'intégrité du document n'est pas validée car la somme de contrôle est invalide : %s"
                    % given_checksum.hex()
                ]
            }
        )

    return jsonify({"checksum": given_checksum.hex()}), 200


def _ask_for_validation(offerer: Offerer, user_offerer: UserOfferer):
    try:
        maybe_send_offerer_validation_email(offerer, user_offerer, send_raw_email)

    except MailServiceException as mail_service_exception:
        app.logger.exception("Email service failure", mail_service_exception)


def _validate_offerer(offerer: Offerer, user_offerer: UserOfferer):
    offerer.validationToken = None
    user_offerer.validationToken = None
    repository.save(offerer, user_offerer)
