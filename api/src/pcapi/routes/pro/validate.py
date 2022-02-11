import logging

from pcapi.core.mails.transactional.pro.welcome_to_pro import send_welcome_to_pro_email
from pcapi.core.offerers import api
from pcapi.core.offerers.exceptions import ValidationTokenNotFoundError
from pcapi.domain.admin_emails import maybe_send_offerer_validation_email
from pcapi.models.api_errors import ResourceNotFoundError
from pcapi.repository import repository
from pcapi.repository import user_offerer_queries
from pcapi.repository import user_queries
from pcapi.serialization.decorator import spectree_serialize
from pcapi.validation.routes.validate import check_valid_token_for_user_validation

from . import blueprint


logger = logging.getLogger(__name__)


@blueprint.pro_public_api_v1.route("/validate/user-offerer/<token>", methods=["GET"])
@spectree_serialize(on_success_status=202, json_format=False)
def validate_offerer_attachment(token) -> str:
    try:
        api.validate_offerer_attachment(token)
    except ValidationTokenNotFoundError:
        errors = ResourceNotFoundError()
        errors.add_error(
            "validation", "Aucun(e) objet ne correspond à ce code de validation" + " ou l'objet est déjà validé"
        )
        raise errors

    return "Validation du rattachement de la structure effectuée"


@blueprint.pro_public_api_v1.route("/validate/offerer/<token>", methods=["GET"])
@spectree_serialize(on_success_status=202, json_format=False)
def validate_new_offerer(token) -> str:
    try:
        api.validate_offerer(token)
    except ValidationTokenNotFoundError:
        errors = ResourceNotFoundError()
        errors.add_error(
            "validation", "Aucun(e) objet ne correspond à ce code de validation" + " ou l'objet est déjà validé"
        )
        raise errors
    return "Validation effectuée"


@blueprint.pro_private_api.route("/validate/user/<token>", methods=["PATCH"])
@spectree_serialize(on_success_status=204)
def validate_user(token) -> None:
    user_to_validate = user_queries.find_by_validation_token(token)
    check_valid_token_for_user_validation(user_to_validate)

    user_to_validate.validationToken = None
    user_to_validate.isEmailValidated = True
    repository.save(user_to_validate)

    if not send_welcome_to_pro_email(user_to_validate):
        logger.warning(
            "Could not send welcome email when pro user is valid",
            extra={"user": user_to_validate.id},
        )

    user_offerer = user_offerer_queries.find_one_or_none_by_user_id(user_to_validate.id)

    if user_offerer:
        offerer = user_offerer.offerer
        if not maybe_send_offerer_validation_email(offerer, user_offerer):
            logger.warning(
                "Could not send offerer validation email to offerer",
                extra={"user_offerer": user_offerer.id},
            )
