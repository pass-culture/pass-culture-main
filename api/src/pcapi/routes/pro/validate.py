import logging

from flask_login import login_required

import pcapi.core.mails.transactional as transactional_mails
from pcapi.core.offerers import api
from pcapi.core.offerers.exceptions import ValidationTokenNotFoundError
import pcapi.core.offerers.models as offerers_models
from pcapi.domain.admin_emails import maybe_send_offerer_validation_email
from pcapi.models.api_errors import ResourceNotFoundError
from pcapi.repository import repository
from pcapi.repository import user_queries
from pcapi.serialization.decorator import spectree_serialize
from pcapi.validation.routes.validate import check_valid_token_for_user_validation

from . import blueprint


logger = logging.getLogger(__name__)


@blueprint.pro_public_api_v1.route("/validate/user-offerer/<token>", methods=["GET"])
@login_required
@spectree_serialize(on_success_status=202, json_format=False)
def validate_offerer_attachment(token) -> str:  # type: ignore [no-untyped-def]
    try:
        api.validate_offerer_attachment(token)
    except ValidationTokenNotFoundError:
        errors = ResourceNotFoundError()
        errors.add_error(
            "validation", "Aucun objet ne correspond à ce code de validation" + " ou l'objet est déjà validé"
        )
        raise errors

    return "Validation du rattachement de la structure effectuée"


@blueprint.pro_public_api_v1.route("/validate/offerer/<token>", methods=["GET"])
@spectree_serialize(on_success_status=202, json_format=False)
def validate_new_offerer(token) -> str:  # type: ignore [no-untyped-def]
    try:
        api.validate_offerer(token)
    except ValidationTokenNotFoundError:
        errors = ResourceNotFoundError()
        errors.add_error(
            "validation", "Aucun objet ne correspond à ce code de validation" + " ou l'objet est déjà validé"
        )
        raise errors
    return "Validation effectuée"


@blueprint.pro_private_api.route("/validate/user/<token>", methods=["PATCH"])
@spectree_serialize(on_success_status=204, api=blueprint.pro_private_schema)
def validate_user(token) -> None:  # type: ignore [no-untyped-def]
    user_to_validate = user_queries.find_by_validation_token(token)
    check_valid_token_for_user_validation(user_to_validate)

    user_to_validate.validationToken = None
    user_to_validate.isEmailValidated = True
    repository.save(user_to_validate)

    if not transactional_mails.send_welcome_to_pro_email(user_to_validate):
        logger.warning(
            "Could not send welcome email when pro user is valid",
            extra={"user": user_to_validate.id},
        )

    user_offerer = offerers_models.UserOfferer.query.filter_by(userId=user_to_validate.id).one_or_none()

    if user_offerer:
        offerer = user_offerer.offerer
        if not maybe_send_offerer_validation_email(offerer, user_offerer):
            logger.warning(
                "Could not send offerer validation email to offerer",
                extra={"user_offerer": user_offerer.id},
            )
