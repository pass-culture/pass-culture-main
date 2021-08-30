from datetime import datetime
import logging

from pcapi.core import search
from pcapi.core.offerers.models import Offerer
from pcapi.domain.admin_emails import maybe_send_offerer_validation_email
from pcapi.domain.user_emails import send_attachment_validation_email_to_pro_offerer
from pcapi.domain.user_emails import send_validation_confirmation_email_to_pro
from pcapi.flask_app import private_api
from pcapi.flask_app import public_api
from pcapi.models import UserOfferer
from pcapi.repository import repository
from pcapi.repository import user_offerer_queries
from pcapi.repository import user_queries
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils.mailing import MailServiceException
from pcapi.validation.routes.users import check_validation_token_has_been_already_used
from pcapi.validation.routes.validate import check_valid_token_for_user_validation
from pcapi.validation.routes.validate import check_validation_request


logger = logging.getLogger(__name__)


@public_api.route("/validate/user-offerer/<token>", methods=["GET"])
@spectree_serialize(on_success_status=202, json_format=False)
def validate_offerer_attachment(token) -> str:
    check_validation_request(token)
    user_offerer = UserOfferer.query.filter_by(validationToken=token).one_or_none()
    check_validation_token_has_been_already_used(user_offerer)

    user_offerer.validationToken = None
    repository.save(user_offerer)

    try:
        send_attachment_validation_email_to_pro_offerer(user_offerer)
    except MailServiceException as mail_service_exception:
        logger.exception(
            "Could not send attachment validation email to offerer", extra={"exc": str(mail_service_exception)}
        )

    return "Validation du rattachement de la structure effectuée"


@public_api.route("/validate/offerer/<token>", methods=["GET"])
@spectree_serialize(on_success_status=202, json_format=False)
def validate_new_offerer(token) -> str:
    check_validation_request(token)
    offerer = Offerer.query.filter_by(validationToken=token).one_or_none()
    check_validation_token_has_been_already_used(offerer)
    offerer.validationToken = None
    offerer.dateValidated = datetime.utcnow()
    managed_venues = offerer.managedVenues

    repository.save(offerer)
    search.async_index_venue_ids([venue.id for venue in managed_venues])

    try:
        send_validation_confirmation_email_to_pro(offerer)
    except MailServiceException as mail_service_exception:
        logger.exception(
            "Could not send validation confirmation email to offerer", extra={"exc": str(mail_service_exception)}
        )
    return "Validation effectuée"


@private_api.route("/validate/user/<token>", methods=["PATCH"])
@spectree_serialize(on_success_status=204)
def validate_user(token) -> None:
    user_to_validate = user_queries.find_by_validation_token(token)
    check_valid_token_for_user_validation(user_to_validate)

    user_to_validate.validationToken = None
    user_to_validate.isEmailValidated = True
    repository.save(user_to_validate)

    user_offerer = user_offerer_queries.find_one_or_none_by_user_id(user_to_validate.id)

    if user_offerer:
        offerer = user_offerer.offerer
        _ask_for_validation(offerer, user_offerer)

    return None


def _ask_for_validation(offerer: Offerer, user_offerer: UserOfferer):
    try:
        maybe_send_offerer_validation_email(offerer, user_offerer)

    except MailServiceException as mail_service_exception:
        logger.exception(
            "Could not send offerer validation email to offerer", extra={"exc": str(mail_service_exception)}
        )
