from flask import current_app as app

from pcapi import settings
from pcapi.connectors import redis
from pcapi.domain.admin_emails import maybe_send_offerer_validation_email
from pcapi.domain.iris import link_valid_venue_to_irises
from pcapi.domain.user_emails import send_attachment_validation_email_to_pro_offerer
from pcapi.domain.user_emails import send_validation_confirmation_email_to_pro
from pcapi.flask_app import private_api
from pcapi.flask_app import public_api
from pcapi.models import Offerer
from pcapi.models import UserOfferer
from pcapi.models.feature import FeatureToggle
from pcapi.repository import feature_queries
from pcapi.repository import repository
from pcapi.repository import user_offerer_queries
from pcapi.repository import user_queries
from pcapi.utils.mailing import MailServiceException
from pcapi.validation.routes.users import check_validation_token_has_been_already_used
from pcapi.validation.routes.validate import check_valid_token_for_user_validation
from pcapi.validation.routes.validate import check_validation_request


# @debt api-migration
@public_api.route("/validate/user-offerer/<token>", methods=["GET"])
def validate_offerer_attachment(token):
    check_validation_request(token)
    user_offerer = UserOfferer.query.filter_by(validationToken=token).first()
    check_validation_token_has_been_already_used(user_offerer)

    user_offerer.validationToken = None
    repository.save(user_offerer)

    try:
        send_attachment_validation_email_to_pro_offerer(user_offerer)
    except MailServiceException as mail_service_exception:
        app.logger.exception("Email service failure", mail_service_exception)

    return "Validation du rattachement de la structure effectuée", 202


# @debt api-migration
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
        send_validation_confirmation_email_to_pro(offerer)
    except MailServiceException as mail_service_exception:
        app.logger.exception("Email service failure", mail_service_exception)
    return "Validation effectuée", 202


# @debt api-migration
@private_api.route("/validate/user/<token>", methods=["PATCH"])
def validate_user(token):
    user_to_validate = user_queries.find_by_validation_token(token)
    check_valid_token_for_user_validation(user_to_validate)

    user_to_validate.validationToken = None
    user_to_validate.isEmailValidated = True
    repository.save(user_to_validate)

    user_offerer = user_offerer_queries.find_one_or_none_by_user_id(user_to_validate.id)

    if user_offerer:
        offerer = user_offerer.offerer

        if settings.IS_INTEGRATION:
            _validate_offerer(offerer, user_offerer)
        else:
            _ask_for_validation(offerer, user_offerer)

    return "", 204


def _ask_for_validation(offerer: Offerer, user_offerer: UserOfferer):
    try:
        maybe_send_offerer_validation_email(offerer, user_offerer)

    except MailServiceException as mail_service_exception:
        app.logger.exception("Email service failure", mail_service_exception)


def _validate_offerer(offerer: Offerer, user_offerer: UserOfferer):
    offerer.validationToken = None
    user_offerer.validationToken = None
    repository.save(offerer, user_offerer)
