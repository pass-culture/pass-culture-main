import logging

from pcapi.connectors import sirene
import pcapi.core.mails.transactional as transactional_mails
import pcapi.core.offerers.models as offerers_models
from pcapi.domain.admin_emails import maybe_send_offerer_validation_email
from pcapi.repository import repository
from pcapi.repository import user_queries
from pcapi.serialization.decorator import spectree_serialize
from pcapi.validation.routes.validate import check_valid_token_for_user_validation

from . import blueprint


logger = logging.getLogger(__name__)


@blueprint.pro_private_api.route("/validate/user/<token>", methods=["PATCH"])
@spectree_serialize(on_success_status=204, api=blueprint.pro_private_schema)
def validate_user(token: str) -> None:
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

        assert offerer.siren  # helps mypy until Offerer.siren is set as NOT NULL
        try:
            siren_info = sirene.get_siren(offerer.siren)
        except sirene.SireneException as exc:
            logger.info("Could not fetch info from Sirene API", extra={"exc": exc})
            siren_info = None

        if not maybe_send_offerer_validation_email(offerer, user_offerer, siren_info):
            logger.warning(
                "Could not send offerer validation email to offerer",
                extra={"user_offerer": user_offerer.id},
            )
